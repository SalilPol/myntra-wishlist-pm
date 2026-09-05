"""
Decision engine for Wishlist Decide.

Every verdict is grounded in structured data the platform already holds:
the user's kept/returned sizes by brand, review size feedback, stock by size,
and the user's stated intent and occasion. The LLM (optional) is used to
write the explanation and styling suggestions from that data, never to invent
facts. If no API key is present, deterministic verdicts are shown instead.
"""
import json
import os
import re
from datetime import date, datetime, timedelta

INTENT_LABELS = {
    "buy_soon": "Buying soon",
    "occasion": "For an occasion",
    "unsure": "Not sure yet",
    "sale_wait": "Waiting for a sale",
    "inspiration": "Just inspiration",
}
INTENT_WEIGHT = {"buy_soon": 1.0, "occasion": 0.9, "unsure": 0.75, "sale_wait": 0.35, "inspiration": 0.05}

SIZE_ORDER = {
    "alpha": ["XS", "S", "M", "L", "XL", "XXL"],
    "waist": ["26", "28", "30", "32", "34", "36"],
    "uk": ["UK3", "UK4", "UK5", "UK6", "UK7", "UK8"],
}


def _scale(sizes):
    keys = list(sizes.keys())
    for name, order in SIZE_ORDER.items():
        if keys[0] in order:
            return order
    return keys


def shift(size, n, sizes):
    """Move n steps along the size scale, staying inside the sizes this item is sold in."""
    order = [k for k in _scale(sizes) if k in sizes]
    if size not in order:
        return size
    i = max(0, min(len(order) - 1, order.index(size) + n))
    return order[i]


def days_to(d):
    return (datetime.strptime(d, "%Y-%m-%d").date() - date.today()).days


# ---------------------------------------------------------------- priority

def priority(item, intent, profile):
    """Which item to decide first. Returns score and a readable breakdown."""
    w_intent = INTENT_WEIGHT.get(intent, 0.5)
    fit = fit_verdict(item, profile)
    stock = item["sizes"].get(fit["size"], 0)
    viability = 0.15 if stock == 0 else 1.0
    urgency = 1.0
    reason_urgency = ""
    if 0 < stock <= 3:
        urgency += 0.25
        reason_urgency = f"only {stock} left in {fit['size']}"
    if intent == "occasion":
        soon = [o for o in profile["occasions"] if 0 <= days_to(o["date"]) <= 45]
        if soon:
            o = min(soon, key=lambda x: days_to(x["date"]))
            urgency += 0.25
            reason_urgency = (reason_urgency + "; " if reason_urgency else "") + f"{o['name']} in {days_to(o['date'])} days"
    recency = max(0.6, 1 - item["saved_days_ago"] / 120)
    confidence_bonus = {"high": 0.15, "medium": 0.05, "low": 0.0}[fit["confidence"]]
    score = w_intent * viability * urgency * recency + confidence_bonus
    return {
        "score": round(score, 3),
        "breakdown": {
            "intent": f"{INTENT_LABELS.get(intent, intent)} (x{w_intent})",
            "viability": "in stock in your size" if stock else "your size is sold out (x0.15)",
            "urgency": reason_urgency or "no deadline",
            "recency": f"saved {item['saved_days_ago']} days ago",
            "fit_confidence": fit["confidence"],
        },
        "fit": fit,
    }


# ---------------------------------------------------------------- fit

def fit_verdict(item, profile):
    """Deterministic size verdict from the user's own history plus review size feedback.

    Rules: exact brand+type history beats brand history beats type history beats usual size.
    At most one size adjustment is applied (brand note OR review signal), never both.
    Sizes never leave the range this item is sold in.
    """
    hist = profile["fit_history"]
    sizes = item["sizes"]
    reasons, shifted = [], False

    exact = [h for h in hist if h["brand"] == item["brand"] and h["sub"] == item["sub"]]
    brand = [h for h in hist if h["brand"] == item["brand"] and h["category"] == item["category"]]
    same_type = [h for h in hist if h["category"] == item["category"] and h["sub"] == item["sub"]]

    kept_exact = [h for h in exact if h["outcome"] == "kept"]
    ret_exact = [h for h in exact if h["outcome"] == "returned"]
    kept_brand = [h for h in brand if h["outcome"] == "kept"]
    ret_brand = [h for h in brand if h["outcome"] == "returned"]
    kept_type = [h for h in same_type if h["outcome"] == "kept"]

    if kept_exact:
        base, conf = kept_exact[-1]["size"], "high"
        reasons.append(f"You kept a {item['brand']} {item['sub']} in {base}.")
        shifted = True  # trust the exact match, do not adjust further
    elif ret_exact:
        r = ret_exact[-1]
        n = +1 if re.search(r"tight|small", r.get("reason", "")) else -1
        base, conf, shifted = shift(r["size"], n, sizes), "medium", True
        reasons.append(f"You returned a {item['brand']} {item['sub']} in {r['size']} ({r.get('reason', 'fit')}), so {base} this time.")
    elif kept_brand:
        base, conf, shifted = kept_brand[-1]["size"], "medium", True  # brand history already reflects brand sizing
        reasons.append(f"You kept a {item['brand']} {kept_brand[-1]['sub']} in {base}. Different cut, same brand, so no further adjustment.")
    elif ret_brand:
        r = ret_brand[-1]
        n = +1 if re.search(r"tight|small", r.get("reason", "")) else -1
        base, conf, shifted = shift(r["size"], n, sizes), "medium", True
        reasons.append(f"You returned a {item['brand']} {r['sub']} in {r['size']} ({r.get('reason', 'fit')}), so {base} is the safer start.")
    elif kept_type and item["category"] == "footwear":
        base, conf = kept_type[-1]["size"], "medium"
        reasons.append(f"You kept {kept_type[-1]['brand']} {item['sub']} in {base}.")
    elif kept_type:
        base, conf = profile["usual_top_size"], "medium"
        reasons.append(f"Starting from your usual size {base}. (You kept a {kept_type[-1]['brand']} {item['sub']} in "
                       f"{kept_type[-1]['size']}, but that brand's sizing differs, so we do not carry it over.)")
    else:
        base = profile["usual_top_size"] if item["category"] != "footwear" else "UK5"
        conf = "low"
        reasons.append(f"No history for {item['brand']} or this type. Starting from your usual size {base}.")

    # cautions from other returns in the same brand, without changing the size
    if kept_exact and ret_brand:
        r = ret_brand[-1]
        reasons.append(f"Note: you returned a {item['brand']} {r['sub']} in {r['size']} ({r.get('reason', 'fit')}).")

    # one adjustment only: brand note first, else review signal
    note = item.get("brand_fit_note", "")
    sf, n_rev = item["reviews"]["size_feedback"], item["reviews"]["count"]
    if not shifted and ("size down" in note or "oversized" in note):
        new = shift(base, -1, sizes)
        if new != base:
            reasons.append(f"{item['brand']} says {note}, so {new} for a regular fit.")
            base, shifted = new, True
    elif not shifted and "small" in note:
        new = shift(base, +1, sizes)
        if new != base:
            reasons.append(f"{item['brand']} {note}, so {new}.")
            base, shifted = new, True
    if not shifted and sf["small"] >= 0.4:
        new = shift(base, +1, sizes)
        if new != base:
            reasons.append(f"{int(sf['small'] * 100)}% of {n_rev} reviewers say it runs small, so {new}.")
            base, shifted = new, True
    elif not shifted and sf["large"] >= 0.3:
        new = shift(base, -1, sizes)
        if new != base:
            reasons.append(f"{int(sf['large'] * 100)}% of {n_rev} reviewers say it runs large, so {new}.")
            base, shifted = new, True
    else:
        reasons.append(f"{int(sf['true'] * 100)}% of {n_rev} reviewers say it fits true to size.")

    stock = sizes.get(base, 0)
    alt = None
    if stock == 0:
        for cand in (shift(base, +1, sizes), shift(base, -1, sizes)):
            if sizes.get(cand, 0) > 0:
                alt = cand
                break
    return {"size": base, "confidence": conf, "reasons": reasons, "stock": stock, "alternative": alt,
            "unknown": _fit_unknowns(item, profile)}


def _fit_unknowns(item, profile):
    u = []
    if item["sub"] in ("dress", "kurta set") and profile.get("height_cm", 0) < 163:
        u.append("Hem length on your height. Reviews mention it runs long on 5'3\" and under.")
    if item["sub"] == "jeans":
        u.append("Inseam length. Several reviewers hemmed these.")
    return u


# ---------------------------------------------------------------- look and quality

def look_verdict(item, profile):
    fam = {"Sage green": "green", "Emerald": "green", "Mustard": "warm", "Camel": "warm", "Mid blue": "blue",
           "White": "neutral", "Lavender": "cool", "Ecru": "neutral"}.get(item["colour"], "neutral")
    pairings = [w["item"] for w in profile["wardrobe"] if w["colour_family"] in ("neutral", fam)]
    r = item["reviews"]
    colour_note = (f"{int(r['colour_accuracy'] * 100)}% of reviewers say the colour matches the photos."
                   if r["colour_accuracy"] >= 0.8 else
                   f"Only {int(r['colour_accuracy'] * 100)}% of reviewers say the colour matches the photos. Expect it darker or warmer in person.")
    return {"pairings": pairings[:3], "colour_note": colour_note, "photo_reviews": r["photo_reviews"],
            "snippets": r["snippets"]}


def quality_note(item):
    r = item["reviews"]
    ok = r["fabric_ok"]
    level = "Reviewers are happy with the fabric" if ok >= 0.8 else "Fabric gets mixed reviews" if ok >= 0.65 else "Fabric is the main complaint"
    return f"{level} ({int(ok * 100)}% positive on material). {item['material']}."


# ---------------------------------------------------------------- decide-by

def decide_by(item, intent, profile):
    if intent == "occasion":
        soon = [o for o in profile["occasions"] if days_to(o["date"]) >= 0]
        if soon:
            o = min(soon, key=lambda x: days_to(x["date"]))
            latest = datetime.strptime(o["date"], "%Y-%m-%d").date() - timedelta(days=7)
            return {"date": latest.isoformat(), "why": f"Order by then to have it a week before {o['name']}, with time for an exchange."}
    stock = item["sizes"]
    low = [s for s, n in stock.items() if 0 < n <= 3]
    if low:
        return {"date": (date.today() + timedelta(days=3)).isoformat(), "why": f"Low stock in {', '.join(low)}. Not a discount, just the truth about inventory."}
    return {"date": (date.today() + timedelta(days=14)).isoformat(), "why": "Two weeks is enough to get a friend's view and decide. After that this goes back to inspiration."}


# ---------------------------------------------------------------- share card

def share_card(item, fit, base_url, other=None):
    lines = [f"Should I get this? {item['brand']} {item['name']}, {item['colour']}, Rs {item['price']:,}. "
             f"Size {fit['size']} ({fit['confidence']} confidence)."]
    if other:
        lines.append(f"Or this one: {other['brand']} {other['name']}, {other['colour']}, Rs {other['price']:,}.")
    link = f"{base_url}?vote={item['id']}" + (f"&vs={other['id']}" if other else "")
    lines.append(f"Tap to vote (10 seconds): {link}")
    return "\n".join(lines), link


# ---------------------------------------------------------------- LLM explanation (optional)

SYSTEM = """You are a shopping assistant inside a fashion app. You receive structured facts about one wishlisted item,
the shopper's own fit history, wardrobe, and the deterministic verdicts already computed. Write the explanation a
trusted friend who works in fashion retail would give. Use ONLY the facts provided. Never invent reviews, stock, or
history. If the data is thin, say so plainly. Respond with JSON only:
{"fit_explanation": str (2 to 3 sentences, name the recommended size and the single strongest reason),
 "look_advice": str (2 sentences, concrete pairings from the wardrobe list, mention colour caveat if any),
 "quality_line": str (1 sentence),
 "decision_prompt": str (1 sentence that helps the shopper decide, not a sales push; may recommend NOT buying),
 "still_unknown": [str] (0 to 2 items the data cannot answer)}"""


def llm_explain(item, intent, profile, fit, look, api_key):
    if not api_key:
        return None
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=api_key)
        payload = {
            "item": {k: item[k] for k in ("brand", "name", "category", "sub", "price", "colour", "material", "brand_fit_note", "sizes")},
            "reviews": item["reviews"], "intent": intent, "shopper_height_cm": profile["height_cm"],
            "shopper_fit_history": profile["fit_history"], "wardrobe": profile["wardrobe"],
            "occasions": profile["occasions"], "computed_fit_verdict": fit, "computed_look": look,
        }
        resp = client.messages.create(
            model=os.environ.get("MVP_MODEL", "claude-sonnet-5"), max_tokens=500, system=SYSTEM,
            messages=[{"role": "user", "content": json.dumps(payload)}])
        raw = resp.content[0].text.strip()
        raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
        return json.loads(raw)
    except Exception as e:  # noqa: BLE001
        return {"error": str(e)}
