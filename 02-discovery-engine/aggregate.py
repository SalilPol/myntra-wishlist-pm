"""
Turn classified documents into a ranked opportunity table plus segment cuts.

Usage:
    python aggregate.py --inp data/classified.jsonl --outdir data/

Outputs:
    opportunity_table.csv   one row per blocker, ranked by opportunity score
    segment_matrix.csv      blocker share by segment field value
    workarounds.csv         top workarounds and outside-app behaviours
    evidence.jsonl          up to 25 audited quotes per blocker
    summary.json            headline numbers for the dashboard and deck

Opportunity score = frequency_share x mean_severity x addressable_without_money x latency_impact
Frequency and severity come from the data. The last two are analyst weights from taxonomy.py
and are printed alongside so a reader can disagree with them.
"""
import argparse
import json
from collections import Counter, defaultdict

import pandas as pd

from taxonomy import BLOCKERS, SEGMENT_FIELDS


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--inp", required=True)
    ap.add_argument("--outdir", default="data/")
    args = ap.parse_args()

    with open(args.inp, encoding="utf-8") as f:
        docs = [json.loads(l) for l in f if l.strip()]
    rel = [d for d in docs if d.get("analysis", {}).get("relevant")]
    n_rel = max(1, len(rel))

    # blocker frequency, severity, wishlist co-mention
    freq, sev_sum, sev_n, wl_co, decisive = Counter(), Counter(), Counter(), Counter(), Counter()
    evidence = defaultdict(list)
    for d in rel:
        a = d["analysis"]
        seen = set()
        for b in a.get("blockers", []):
            c = b["category"]
            if c in seen:
                continue
            seen.add(c)
            freq[c] += 1
            sev_sum[c] += b.get("severity", 1)
            sev_n[c] += 1
            if a.get("wishlist_mentioned"):
                wl_co[c] += 1
            if b.get("severity", 1) == 3:
                decisive[c] += 1
            if len(evidence[c]) < 25:
                evidence[c].append({"id": d["id"], "source": d["source"], "severity": b.get("severity"),
                                    "evidence": b.get("evidence", "")[:200]})

    rows = []
    for c, spec in BLOCKERS.items():
        share = freq[c] / n_rel
        msev = (sev_sum[c] / sev_n[c]) if sev_n[c] else 0
        score = share * msev * spec["addressable_without_money"] * spec["latency_impact"]
        rows.append({
            "blocker": c, "label": spec["label"], "mentions": freq[c],
            "share_of_relevant_docs": round(share, 3), "mean_severity": round(msev, 2),
            "decisive_mentions": decisive[c],
            "wishlist_co_mentions": wl_co[c],
            "addressable_without_money": spec["addressable_without_money"],
            "latency_impact": spec["latency_impact"],
            "opportunity_score": round(score, 4),
        })
    opp = pd.DataFrame(rows).sort_values("opportunity_score", ascending=False)
    opp["rank"] = range(1, len(opp) + 1)
    opp.to_csv(f"{args.outdir}/opportunity_table.csv", index=False)

    # segment matrix: for each segment field value, blocker share
    seg_rows = []
    for field in SEGMENT_FIELDS:
        by_val = defaultdict(Counter)
        n_val = Counter()
        for d in rel:
            v = d["analysis"].get("segment", {}).get(field, "unknown")
            n_val[v] += 1
            for c in {b["category"] for b in d["analysis"].get("blockers", [])}:
                by_val[v][c] += 1
        for v, cnt in by_val.items():
            for c in BLOCKERS:
                seg_rows.append({"segment_field": field, "segment_value": v, "n_docs": n_val[v],
                                 "blocker": c, "share": round(cnt[c] / max(1, n_val[v]), 3)})
    pd.DataFrame(seg_rows).to_csv(f"{args.outdir}/segment_matrix.csv", index=False)

    # workarounds and outside-app behaviour
    wa = Counter(d["analysis"].get("workaround", "").strip().lower() for d in rel)
    oa = Counter(d["analysis"].get("outside_app_behavior", "").strip().lower() for d in rel)
    wa.pop("", None)
    oa.pop("", None)
    pd.DataFrame(
        [{"type": "workaround", "text": k, "count": v} for k, v in wa.most_common(40)] +
        [{"type": "outside_app", "text": k, "count": v} for k, v in oa.most_common(40)]
    ).to_csv(f"{args.outdir}/workarounds.csv", index=False)

    with open(f"{args.outdir}/evidence.jsonl", "w", encoding="utf-8") as f:
        for c, items in evidence.items():
            for it in items:
                it["blocker"] = c
                f.write(json.dumps(it, ensure_ascii=False) + "\n")

    intents = Counter(d["analysis"].get("intent_type", "unknown") for d in rel)
    sources = Counter(d["source"] for d in docs)
    summary = {
        "total_docs": len(docs), "relevant_docs": len(rel),
        "relevance_rate": round(len(rel) / max(1, len(docs)), 3),
        "wishlist_mentioned_docs": sum(1 for d in rel if d["analysis"].get("wishlist_mentioned")),
        "intent_distribution": dict(intents), "sources": dict(sources),
        "mode": docs[0]["analysis"].get("mode") if docs else None,
        "top3": opp.head(3)[["blocker", "label", "opportunity_score", "share_of_relevant_docs"]].to_dict("records"),
    }
    with open(f"{args.outdir}/summary.json", "w") as f:
        json.dump(summary, f, indent=2)

    print(opp[["rank", "label", "mentions", "share_of_relevant_docs", "mean_severity", "opportunity_score"]].to_string(index=False))
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
