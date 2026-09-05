"""
Collect YouTube comments from Myntra haul and try-on videos.

Usage:
    YOUTUBE_API_KEY=... python collect/youtube.py --videos 25 --out data/raw_youtube.jsonl

Get a free key: Google Cloud Console > APIs > YouTube Data API v3.
Daily quota (10,000 units) covers roughly 25 videos x 200 comments.
"""
import argparse
import json
import os
import time

import requests

API = "https://www.googleapis.com/youtube/v3"
QUERIES = ["myntra haul", "myntra try on haul", "myntra EORS haul",
           "myntra honest review", "myntra kurti haul", "myntra western wear haul"]


def search_videos(key, q, n):
    r = requests.get(f"{API}/search", params={
        "part": "snippet", "q": q, "type": "video", "maxResults": n,
        "regionCode": "IN", "relevanceLanguage": "en", "key": key}, timeout=20)
    r.raise_for_status()
    return [(i["id"]["videoId"], i["snippet"]["title"]) for i in r.json().get("items", [])]


def comments(key, vid, max_pages=2):
    out, token = [], None
    for _ in range(max_pages):
        r = requests.get(f"{API}/commentThreads", params={
            "part": "snippet", "videoId": vid, "maxResults": 100,
            "textFormat": "plainText", "pageToken": token, "key": key}, timeout=20)
        if r.status_code != 200:
            break
        j = r.json()
        for it in j.get("items", []):
            s = it["snippet"]["topLevelComment"]["snippet"]
            if len(s["textDisplay"].strip()) >= 25:
                out.append({"id": f"yt_{it['id']}", "text": s["textDisplay"].strip(),
                            "date": s["publishedAt"], "likes": s.get("likeCount", 0)})
        token = j.get("nextPageToken")
        if not token:
            break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--videos", type=int, default=25)
    ap.add_argument("--out", default="data/raw_youtube.jsonl")
    args = ap.parse_args()
    key = os.environ.get("YOUTUBE_API_KEY")
    if not key:
        raise SystemExit("Set YOUTUBE_API_KEY")

    per_q = max(1, args.videos // len(QUERIES))
    n = 0
    with open(args.out, "w", encoding="utf-8") as f:
        for q in QUERIES:
            for vid, title in search_videos(key, q, per_q):
                for c in comments(key, vid):
                    c.update({"source": "youtube", "rating": None,
                              "meta": {"video_id": vid, "video_title": title, "query": q}})
                    f.write(json.dumps(c, ensure_ascii=False) + "\n")
                    n += 1
                time.sleep(0.5)
    print(f"wrote {n} comments to {args.out}")


if __name__ == "__main__":
    main()
