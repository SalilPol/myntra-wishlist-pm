"""
Collect Reddit posts and comments about Myntra wishlists and buying decisions.

Usage:
    python collect/reddit.py --out data/raw_reddit.jsonl

Uses Reddit's public JSON endpoints (no OAuth). Reddit rate-limits aggressive
callers, so keep the sleep. If you get HTTP 429, wait ten minutes and rerun.
Subreddits and queries are a starting list; add more as you find them.
"""
import argparse
import json
import time

import requests

HEADERS = {"User-Agent": "wishlist-discovery-research/0.1 (contact: your-email@example.com)"}

SUBREDDITS = [
    "IndianFashionAddicts", "india", "IndiaSpeaks", "mumbai", "bangalore",
    "delhi", "IndianSkincareAddicts", "onlineshopping", "indiasocial",
]
QUERIES = [
    "myntra wishlist", "myntra size", "myntra sizing", "myntra fit",
    "myntra return", "myntra EORS", "myntra sale wait", "myntra vs ajio",
    "should I buy myntra", "myntra quality",
]


def fetch_comments(permalink):
    url = f"https://www.reddit.com{permalink}.json?limit=200"
    r = requests.get(url, headers=HEADERS, timeout=20)
    if r.status_code != 200:
        return []
    out = []
    try:
        listing = r.json()[1]["data"]["children"]
    except (IndexError, KeyError, ValueError):
        return []
    for c in listing:
        d = c.get("data", {})
        body = (d.get("body") or "").strip()
        if len(body) >= 25:
            out.append({"id": f"rc_{d.get('id')}", "text": body, "date": d.get("created_utc"),
                        "score": d.get("score")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/raw_reddit.jsonl")
    ap.add_argument("--with-comments", action="store_true", default=True)
    args = ap.parse_args()

    seen, n = set(), 0
    with open(args.out, "w", encoding="utf-8") as f:
        for sub in SUBREDDITS:
            for q in QUERIES:
                url = (f"https://www.reddit.com/r/{sub}/search.json?q={requests.utils.quote(q)}"
                       f"&restrict_sr=1&sort=relevance&t=all&limit=100")
                r = requests.get(url, headers=HEADERS, timeout=20)
                time.sleep(2)
                if r.status_code != 200:
                    print(f"{sub}/{q}: HTTP {r.status_code}")
                    continue
                for p in r.json().get("data", {}).get("children", []):
                    d = p["data"]
                    if d["id"] in seen:
                        continue
                    seen.add(d["id"])
                    text = (d.get("title", "") + ". " + (d.get("selftext") or "")).strip()
                    if len(text) < 25:
                        continue
                    f.write(json.dumps({
                        "id": f"rp_{d['id']}", "source": "reddit", "text": text,
                        "rating": None, "date": d.get("created_utc"),
                        "meta": {"subreddit": sub, "query": q, "score": d.get("score"),
                                 "permalink": d.get("permalink")},
                    }, ensure_ascii=False) + "\n")
                    n += 1
                    if args.with_comments:
                        for c in fetch_comments(d.get("permalink", "")):
                            c.update({"source": "reddit_comment", "rating": None,
                                      "meta": {"subreddit": sub, "parent": d["id"]}})
                            f.write(json.dumps(c, ensure_ascii=False) + "\n")
                            n += 1
                        time.sleep(1.5)
    print(f"wrote {n} documents to {args.out}")


if __name__ == "__main__":
    main()
