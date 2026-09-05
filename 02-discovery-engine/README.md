# Wishlist Discovery Engine (Part 1)

Reads public conversations about shopping on Myntra, tags each one against a
twelve-blocker taxonomy, and ranks opportunity areas by frequency, severity,
and whether they can be fixed without spending money.

## What it does that sentiment analysis does not

| Sentiment analysis | This engine |
|---|---|
| "62% of reviews are negative" | "Fit uncertainty is the decisive reason in 31% of purchase-decision texts, mean severity 2.1, and users cope by ordering two sizes" |
| One label per document | Multiple blockers per document, each with severity and a verbatim quote |
| No segment view | Blocker shares by category, gender, age band, price band, tenure |
| No link to the constraint | Opportunity score explicitly discounts blockers that need money (price waits) and rewards those that shorten the 30-day window |

## Run it (real data)

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...

# 1. Collect (each writes a JSONL into data/)
python collect/playstore.py --count 3000
python collect/appstore.py --pages 10
python collect/reddit.py
YOUTUBE_API_KEY=... python collect/youtube.py --videos 25

# 2. Classify with Claude (cheap: Haiku by default, roughly Rs 150 to 300 for 3,000 docs)
python classify.py --mode llm --inputs "data/raw_*.jsonl" --out data/classified.jsonl
#    Try 100 docs first:  --limit 100

# 3. Aggregate into the opportunity table, segment matrix, workarounds, evidence
python aggregate.py --inp data/classified.jsonl --outdir data/

# 4. Look at it
streamlit run app.py
```

`classify.py` resumes if interrupted, so you can stop and restart safely.

## Offline run (no API key)

```bash
python build_corpus.py --n 400
python classify.py --mode heuristic --inputs data/corpus.jsonl --out data/classified.jsonl
python aggregate.py --inp data/classified.jsonl --outdir data/
streamlit run app.py
```

Heuristic classification is keyword-based and lower precision than the LLM mode.

## Deploy the public link (Streamlit Community Cloud, free)

1. Push this whole repository to GitHub (public or private, both work).
2. Go to share.streamlit.io, sign in with GitHub, click New app.
3. Repository: your repo. Branch: main. Main file path: `02-discovery-engine/app.py`.
4. Advanced settings > Secrets, paste:
   ```
   ANTHROPIC_API_KEY = "sk-ant-..."
   ```
5. Deploy. You get a URL like `https://<name>.streamlit.app`. That is your Part 1 link.

Commit the `data/` outputs from your real run before deploying so the dashboard
loads them. The live classifier tab works for any tester once the secret is set.

## Files

```
taxonomy.py                 blocker definitions, keywords, analyst weights (single source of truth)
collect/playstore.py        Google Play reviews, no key
collect/appstore.py         App Store reviews via Apple RSS, no key
collect/reddit.py           Reddit posts and comments via public JSON, no key
collect/youtube.py          YouTube comments, needs free Data API key
classify.py                 LLM structured extraction (Claude) with heuristic fallback, resumable
aggregate.py                opportunity scoring, segment matrix, workarounds, evidence audit trail
app.py                      Streamlit dashboard + live classifier (the deliverable link)
build_corpus.py             template-based corpus builder for offline runs
```

## Adjusting the analyst weights

`addressable_without_money` and `latency_impact` in `taxonomy.py` are judgment
calls. The dashboard prints them next to the data so a reviewer can rerun the
ranking with different values. If you change them, say so in the deck.

## Known limits, state them in the deck

- App reviews over-represent angry users and app bugs; the relevance filter drops most of those.
- Reddit skews metro, English-speaking, 20 to 35. Tier 2 and 3 voices are thin.
- Segment cues are sparse in short texts; expect most segment fields to be "unknown". Interviews fill this gap.
- Classification is probabilistic. Spot check 50 documents by hand and report agreement.
