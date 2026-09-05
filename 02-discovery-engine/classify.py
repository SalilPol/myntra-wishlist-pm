"""
Classify every collected document against the blocker taxonomy.

Usage:
    # Real run (needs ANTHROPIC_API_KEY):
    python classify.py --mode llm --inputs data/raw_*.jsonl --out data/classified.jsonl

    # Offline run with no API key (keyword heuristics, lower precision):
    python classify.py --mode heuristic --inputs data/corpus.jsonl --out data/classified.jsonl

Each output line = input doc + "analysis" block:
    relevant, wishlist_mentioned, intent_type, blockers[{category, severity, evidence}],
    workaround, outside_app_behavior, segment{...}, sentiment, confidence

The LLM prompt forces JSON only and quotes evidence verbatim from the text so
you can audit any classification back to its source line.
"""
import argparse
import glob
import json
import os
import re
import sys
import time

from taxonomy import BLOCKERS, INTENT_TYPES, SEGMENT_FIELDS

MODEL = os.environ.get("CLASSIFIER_MODEL", "claude-haiku-4-5-20251001")

SYSTEM_PROMPT = f"""You are a product research analyst studying why users of Myntra (Indian fashion e-commerce)
save items to their wishlist but do not buy them within 30 days.

You will receive one user-generated text (an app review, Reddit post or comment, or YouTube comment).
Extract a structured analysis. Respond with JSON only. No prose, no markdown fences.

Blocker categories (use these exact keys):
{json.dumps({k: v["desc"] for k, v in BLOCKERS.items()}, indent=1)}

Intent types: {INTENT_TYPES}
Segment fields and allowed values: {json.dumps(SEGMENT_FIELDS)}

Rules:
- relevant = true only if the text says something about deciding whether to buy fashion items online,
  saving/wishlisting, sizing, returns, comparing, waiting, or similar purchase-decision behaviour.
  Generic app complaints (login bugs, ads) are relevant = false with empty blockers.
- A text can have several blockers. severity: 1 = mentioned in passing, 2 = clearly a reason for not buying,
  3 = stated as the decisive reason or caused a lost purchase.
- evidence must be a verbatim substring of the input text, at most 20 words.
- Infer segment values only from explicit cues (for example "my kurti" implies ethnic_wear; "I am 23" implies 18-24).
  Otherwise use "unknown". Never guess gender from name alone.
- workaround: what the user does to cope (order two sizes, ask a friend, check Amazon, wait for EORS). Empty string if none.
- outside_app_behavior: anything they do outside the app before deciding. Empty string if none.
- sentiment: negative, neutral, or positive.
- confidence: 0 to 1, your confidence in the overall classification.

Output schema:
{{"relevant": bool, "wishlist_mentioned": bool, "intent_type": str, "blockers": [{{"category": str, "severity": int, "evidence": str}}],
 "workaround": str, "outside_app_behavior": str, "segment": {{"gender": str, "age_band": str, "city_tier": str, "category": str, "price_band": str, "tenure": str}},
 "sentiment": str, "confidence": float}}"""


def heuristic(text: str) -> dict:
    """Keyword classifier. Used as a no-key fallback."""
    t = text.lower()
    blockers = []
    for key, spec in BLOCKERS.items():
        hits = [k for k in spec["keywords"] if k in t]
        if hits:
            sev = 1 if len(hits) == 1 else (2 if len(hits) == 2 else 3)
            # find a short evidence window around the first hit
            i = t.find(hits[0])
            evidence = text[max(0, i - 40): i + 60].strip()
            blockers.append({"category": key, "severity": sev, "evidence": evidence})
    intent = "unknown"
    if any(w in t for w in ["wait for sale", "waiting for sale", "eors", "price drop", "until sale"]):
        intent = "sale_wait"
    elif any(w in t for w in ["wedding", "trip", "diwali", "next month", "occasion"]):
        intent = "occasion"
    elif any(w in t for w in ["inspiration", "mood board", "just saving", "just save", "for later"]):
        intent = "inspiration"
    elif any(w in t for w in ["not sure", "unsure", "confused", "should i"]):
        intent = "unsure"
    elif any(w in t for w in ["buying", "will buy", "ordered", "bought"]):
        intent = "buy_soon"
    seg = {k: "unknown" for k in SEGMENT_FIELDS}
    if any(w in t for w in ["kurti", "kurta", "saree", "lehenga", "ethnic"]):
        seg["category"] = "ethnic_wear"
    elif any(w in t for w in ["shoes", "sneaker", "sandal", "heels", "footwear"]):
        seg["category"] = "footwear"
    elif any(w in t for w in ["dress", "top", "jeans", "shirt", "t-shirt", "tshirt", "jacket"]):
        seg["category"] = "western_wear"
    m = re.search(r"\b(1[89]|2[0-9]|3[0-9]|4[0-9])\s*(?:yo|years old|yr|f|m)\b", t)
    if m:
        a = int(m.group(1))
        seg["age_band"] = "18-24" if a < 25 else "25-34" if a < 35 else "35-44" if a < 45 else "45+"
    if re.search(r"\b\d{2}\s*f\b", t) or " she " in t or "my kurti" in t:
        seg["gender"] = "female"
    elif re.search(r"\b\d{2}\s*m\b", t):
        seg["gender"] = "male"
    workaround = ""
    for w in ["order two sizes", "ordered 2 sizes", "two sizes", "ask my", "asked my",
              "check on amazon", "checked amazon", "wait for", "screenshot"]:
        if w in t:
            workaround = w
            break
    outside = ""
    for w in ["youtube", "instagram", "whatsapp", "amazon", "flipkart", "ajio", "store", "friend"]:
        if w in t:
            outside = w
            break
    neg = any(w in t for w in ["bad", "worst", "never", "disappoint", "poor", "waste", "cheap", "fake"])
    pos = any(w in t for w in ["love", "great", "good", "perfect", "happy", "nice"])
    sentiment = "negative" if neg and not pos else "positive" if pos and not neg else "neutral"
    return {
        "relevant": bool(blockers),
        "wishlist_mentioned": "wishlist" in t or "saved" in t or "save" in t,
        "intent_type": intent,
        "blockers": blockers,
        "workaround": workaround,
        "outside_app_behavior": outside,
        "segment": seg,
        "sentiment": sentiment,
        "confidence": 0.4,
    }


def llm(text: str, client) -> dict:
    for attempt in range(4):
        try:
            resp = client.messages.create(
                model=MODEL, max_tokens=600, system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": text[:3000]}],
            )
            raw = resp.content[0].text.strip()
            raw = re.sub(r"^```(?:json)?|```$", "", raw, flags=re.M).strip()
            out = json.loads(raw)
            # sanitise category names the model may drift on
            out["blockers"] = [b for b in out.get("blockers", []) if b.get("category") in BLOCKERS]
            return out
        except Exception as e:  # noqa: BLE001
            wait = 2 ** attempt
            print(f"  retry {attempt + 1} after error: {e} (sleep {wait}s)", file=sys.stderr)
            time.sleep(wait)
    return {"relevant": False, "blockers": [], "confidence": 0, "error": "llm_failed"}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["llm", "heuristic"], default="llm")
    ap.add_argument("--inputs", nargs="+", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=0, help="cap docs for a cheap trial run")
    args = ap.parse_args()

    client = None
    if args.mode == "llm":
        if not os.environ.get("ANTHROPIC_API_KEY"):
            raise SystemExit("ANTHROPIC_API_KEY not set. Use --mode heuristic for a dry run.")
        import anthropic
        client = anthropic.Anthropic()

    paths = [p for pat in args.inputs for p in glob.glob(pat)]
    docs = []
    for p in paths:
        with open(p, encoding="utf-8") as f:
            docs += [json.loads(l) for l in f if l.strip()]
    if args.limit:
        docs = docs[: args.limit]
    print(f"classifying {len(docs)} docs from {len(paths)} files in {args.mode} mode")

    done = set()
    if os.path.exists(args.out):  # resume support
        with open(args.out, encoding="utf-8") as f:
            done = {json.loads(l)["id"] for l in f if l.strip()}
        print(f"resuming, {len(done)} already done")

    with open(args.out, "a", encoding="utf-8") as f:
        for i, d in enumerate(docs, 1):
            if d["id"] in done:
                continue
            d["analysis"] = llm(d["text"], client) if args.mode == "llm" else heuristic(d["text"])
            d["analysis"]["mode"] = args.mode
            f.write(json.dumps(d, ensure_ascii=False) + "\n")
            if i % 50 == 0:
                print(f"  {i}/{len(docs)}")
    print(f"done -> {args.out}")


if __name__ == "__main__":
    main()
