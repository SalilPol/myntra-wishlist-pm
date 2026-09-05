# Myntra: Wishlist to Purchase in 30 days

End-to-end working folder for the Growth PM assignment. Product chosen: **Myntra**.

## The argument in five lines

1. The metric counts users who buy **at least one** wishlisted item **within 30 days**. That makes it a top-item, decision-latency problem, not a "convert the whole wishlist" problem.
2. Decomposed into seven stages, the lowest-rate and most sensitive stage is **S4: whether the shopper's blocking uncertainty about her top item ever gets answered**.
3. The discovery engine and interviews say the blocker on the top item is **fit and look, resolved today by ordering two sizes, screenshotting to a friend, or giving up**. Price waiting is real but attached to third-choice items.
4. The wishlist is a **parking lot with no exit ramp**: no intent, no resolution, no decision moment.
5. **Wishlist Decide** adds all three without money: intent tags, a trusted size verdict from the shopper's own history, look and quality answers, an in-app friend vote, and a decide-by moment tied to her own occasion or true stock.

## Deliverables and where they are

| Brief part | Deliverable | Location | Status |
|---|---|---|---|
| 1 | AI discovery engine, testable link | `02-discovery-engine/` (deploy `app.py` to Streamlit Cloud) | Complete; dashboard loads `data/` |
| 2 | Metric decomposition | `01-metric-decomposition/metric_decomposition.md` + `wishlist_funnel_model.xlsx` | Complete, illustrative baselines flagged |
| 3 | User research | `03-user-research/` screener, guide, 6 interviews, synthesis | Complete |
| 4 | Problem definition | `04-problem-definition.md` | Complete |
| 5 | Deployed MVP | `05-mvp/` (deploy `app.py` to Streamlit Cloud) | Code complete, interaction-tested; **deploy for the public link** |
| 6 | Success metrics | `06-success-metrics.md` | Complete |
| 7 | Risks and mitigation | `07-risks-mitigation.md` | Complete |
| Deck | 10 slides, NL Myntra.pdf | `DECK-OUTLINE.md` maps every slide to its source file | Outline ready |
| Deploy | Public links | `DEPLOY.md` | Step-by-step guide |

## Deployment path (both links from one repo)

```
git init && git add . && git commit -m "wishlist decide"
# push to GitHub, then on share.streamlit.io create two apps from the same repo:
#   02-discovery-engine/app.py  -> discovery engine link
#   05-mvp/app.py               -> MVP link
# add ANTHROPIC_API_KEY under Secrets for each (optional for MVP, needed for live LLM classification)
```

Streamlit Community Cloud is free, needs no credit card, and gives a stable public URL.

## Order of work to finish

1. Deploy both apps, paste the MVP public URL into the share-card field, test the vote loop end to end.
2. Build the deck from the files here. Every number has a source file.
