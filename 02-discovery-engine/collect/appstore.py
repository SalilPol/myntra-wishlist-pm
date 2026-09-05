"""
Collect App Store reviews for the Myntra iOS app via the public RSS feed.

Usage:
    python collect/appstore.py --pages 10 --out data/raw_appstore.jsonl

App id 907394059 is Myntra's iOS app id. Verify once in a browser:
https://apps.apple.com/in/app/myntra-fashion-shopping-app/id907394059
No API key needed. Each page returns up to 50 reviews; Apple caps at 10 pages.
"""
import argparse
import json
import time

import requests

APP_ID = "907394059"
URL = "https://itunes.apple.com/in/rss/customerreviews/page={page}/id={app_id}/sortby=mostrecent/json"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pages", type=int, default=10)
    ap.add_argument("--out", default="data/raw_appstore.jsonl")
    args = ap.parse_args()

    n = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for page in range(1, args.pages + 1):
            r = requests.get(URL.format(page=page, app_id=APP_ID), timeout=20)
            if r.status_code != 200:
                print(f"page {page}: HTTP {r.status_code}, stopping")
                break
            entries = r.json().get("feed", {}).get("entry", [])
            if isinstance(entries, dict):
                entries = [entries]
            for e in entries:
                text = (e.get("content", {}).get("label") or "").strip()
                if len(text) < 20:
                    continue
                doc = {
                    "id": f"as_{e.get('id', {}).get('label')}",
                    "source": "app_store",
                    "text": (e.get("title", {}).get("label", "") + ". " + text).strip(),
                    "rating": int(e.get("im:rating", {}).get("label", 0) or 0),
                    "date": e.get("updated", {}).get("label"),
                    "meta": {"version": e.get("im:version", {}).get("label")},
                }
                f.write(json.dumps(doc, ensure_ascii=False) + "\n")
                n += 1
            time.sleep(1)
    print(f"wrote {n} reviews to {args.out}")


if __name__ == "__main__":
    main()
