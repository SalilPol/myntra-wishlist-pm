"""
Build a corpus from templated user statements when live collection is unavailable
(rate limits, no API keys, offline). Output format matches the collectors exactly.

Usage:
    python build_corpus.py --n 400 --out data/corpus.jsonl
"""
import argparse
import json
import random
from datetime import date, timedelta

TEMPLATES = {
    "FIT_SIZE": [
        "Saved a {item} in my wishlist for weeks but not sure if M or L will fit, every brand sizing is different on Myntra.",
        "Size chart says one thing, reviews say it runs small. Kept it in wishlist and never ordered.",
        "Ordered two sizes of the same {item} last time and returned one, cannot keep doing that so I just leave things in wishlist.",
        "I am 27F and I never know my size in {brand}, so half my wishlist is just things I am scared to order.",
    ],
    "LOOK_STYLE": [
        "The {item} looks great on the model but I have no idea how it will look on me, so it sits in wishlist.",
        "Colour in the photo and actual product were totally different last time. Now I hesitate on anything I save.",
        "Not sure what to pair this {item} with, I saved it but probably will not buy.",
    ],
    "QUALITY": [
        "Wishlisted a {brand} {item} but reviews say the fabric is thin and cheap looking. Skipped it.",
        "For 1500 rupees I want to know the material quality before buying, the description does not say much.",
    ],
    "PRICE_WAIT": [
        "I only buy from wishlist during EORS. Everything else waits for a sale.",
        "Waiting for price drop on my wishlist items, Myntra always has an offer coming.",
        "Too expensive right now, saved it and will check during the next sale.",
    ],
    "OCCASION_TIMING": [
        "Saved a lehenga for my cousin's wedding in December. No hurry, will decide next month.",
        "Wishlisted winter jackets in August for a trip. Will buy later.",
    ],
    "AVAILABILITY": [
        "By the time I decided, my size was out of stock. Wishlist just shows sold out now, so annoying.",
        "Half my wishlist items got removed or are unavailable in my size. Why even save.",
        "Waited two days and the {item} was sold out in M. No restock notification either.",
    ],
    "RETURN_HASSLE": [
        "Return pickup failed twice last time, so now I do not order anything I am not 100 percent sure about.",
        "Refund took 12 days. I keep things in wishlist instead of risking another return.",
        "Some items are non returnable and you only notice at checkout. So I just save and abandon.",
    ],
    "DELIVERY_TRUST": [
        "Delivery was late by a week last time. I hesitate to order for occasions now.",
        "Got a wrong item once, since then my wishlist is longer than my orders.",
    ],
    "SOCIAL_VALIDATION": [
        "I screenshot my wishlist and send it to my sister on WhatsApp before buying anything.",
        "Always ask my friend if the {item} looks good before ordering, she takes days to reply lol.",
        "My wife decides. I just wishlist and show her on weekends.",
    ],
    "ALTERNATIVES": [
        "Found the same {brand} {item} cheaper on Ajio, so Myntra wishlist stays as it is.",
        "Confused between three similar dresses in my wishlist, ended up buying none.",
        "I compare on Amazon and Flipkart before buying from Myntra wishlist.",
    ],
    "BOOKMARK_ONLY": [
        "I use wishlist like Pinterest, just saving outfits for inspiration, not buying.",
        "Have 200 items in wishlist, it is basically my mood board for later.",
    ],
    "APP_UX": [
        "Wishlist has no folders or sorting. 150 items and I cannot find anything, so I never revisit it.",
        "Wish the wishlist could remind me or let me add notes about why I saved something.",
        "Too many items in wishlist and no way to compare them side by side.",
    ],
    "NONE": [
        "App keeps crashing on login after the update. Fix it please.",
        "Great app, fast delivery, love the collection.",
        "Customer care did not respond to my query about coupon code.",
        "Too many notifications and ads on the home screen.",
    ],
}
ITEMS = ["kurti", "dress", "pair of jeans", "top", "shirt", "sneakers", "co-ord set", "jacket"]
BRANDS = ["H&M", "Roadster", "Libas", "Levis", "Anouk", "Zara", "Puma", "Sassafras"]
SOURCES = ["play_store", "app_store", "reddit", "youtube"]

# Prior over blockers used when building from templates.
WEIGHTS = {"FIT_SIZE": 18, "LOOK_STYLE": 12, "QUALITY": 8, "PRICE_WAIT": 16, "OCCASION_TIMING": 6,
           "AVAILABILITY": 9, "RETURN_HASSLE": 8, "DELIVERY_TRUST": 4, "SOCIAL_VALIDATION": 7,
           "ALTERNATIVES": 6, "BOOKMARK_ONLY": 5, "APP_UX": 7, "NONE": 14}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=400)
    ap.add_argument("--out", default="data/corpus.jsonl")
    ap.add_argument("--seed", type=int, default=7)
    args = ap.parse_args()
    random.seed(args.seed)
    cats, w = zip(*WEIGHTS.items())
    with open(args.out, "w", encoding="utf-8") as f:
        for i in range(args.n):
            primary = random.choices(cats, weights=w)[0]
            text = random.choice(TEMPLATES[primary]).format(item=random.choice(ITEMS), brand=random.choice(BRANDS))
            if primary != "NONE" and random.random() < 0.3:  # second blocker
                second = random.choice([c for c in cats if c not in (primary, "NONE")])
                text += " " + random.choice(TEMPLATES[second]).format(item=random.choice(ITEMS), brand=random.choice(BRANDS))
            src = random.choices(SOURCES, weights=[45, 15, 25, 15])[0]
            prefix = {"play_store": "ps", "app_store": "as", "reddit": "rp", "youtube": "yt"}[src]
            f.write(json.dumps({
                "id": f"{prefix}_{i:05d}", "source": src,
                "text": text, "rating": random.choice([1, 2, 3, 4, 5]) if src in ("play_store", "app_store") else None,
                "date": (date.today() - timedelta(days=random.randint(1, 120))).isoformat(),
                "meta": {},
            }, ensure_ascii=False) + "\n")
    print(f"wrote {args.n} docs to {args.out}")


if __name__ == "__main__":
    main()
