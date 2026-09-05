"""
Collect Google Play reviews for the Myntra Android app.

Usage:
    python collect/playstore.py --count 3000 --out data/raw_playstore.jsonl

Package id: com.myntra.android
No API key needed. Pulls newest first; filter to wishlist-relevant later.
"""
import argparse
import json
from datetime import datetime

from google_play_scraper import Sort, reviews

APP_ID = "com.myntra.android"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=2000)
    ap.add_argument("--out", default="data/raw_playstore.jsonl")
    ap.add_argument("--lang", default="en")
    ap.add_argument("--country", default="in")
    args = ap.parse_args()

    result, _ = reviews(
        APP_ID,
        lang=args.lang,
        country=args.country,
        sort=Sort.NEWEST,
        count=args.count,
    )

    n = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for r in result:
            text = (r.get("content") or "").strip()
            if len(text) < 20:
                continue
            doc = {
                "id": f"ps_{r['reviewId']}",
                "source": "play_store",
                "text": text,
                "rating": r.get("score"),
                "date": r["at"].isoformat() if isinstance(r.get("at"), datetime) else str(r.get("at")),
                "meta": {"app_version": r.get("reviewCreatedVersion"), "thumbs_up": r.get("thumbsUpCount")},
            }
            f.write(json.dumps(doc, ensure_ascii=False) + "\n")
            n += 1
    print(f"wrote {n} reviews to {args.out}")


if __name__ == "__main__":
    main()
