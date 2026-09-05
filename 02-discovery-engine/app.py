"""
Wishlist Discovery Engine dashboard.

Run locally:   streamlit run app.py
Deploy:        Streamlit Community Cloud (see README.md). Add ANTHROPIC_API_KEY in secrets
               to enable the live classifier; the dashboard works without it.

Reads whatever is in data/ (opportunity_table.csv, segment_matrix.csv, workarounds.csv,
evidence.jsonl, summary.json). Rerun aggregate.py after every new classification run.
"""
import json
import os
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

from classify import SYSTEM_PROMPT, _text_of, heuristic
from taxonomy import BLOCKERS, SEGMENT_FIELDS

DATA = Path(__file__).parent / "data"

st.set_page_config(page_title="Wishlist Discovery Engine", page_icon="🔎", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.6rem; max-width: 1200px;}
  h1, h2, h3 {font-family: Georgia, 'Times New Roman', serif; letter-spacing: -0.01em;}
  .note {background:#F3F6F9; color:#1C1B22; border-left: 4px solid #2B6CB0; padding: .7rem 1rem; border-radius: 4px;}
  .warn {background:#FFF7E6; color:#1C1B22; border-left: 4px solid #B7791F; padding: .7rem 1rem; border-radius: 4px;}
</style>
""", unsafe_allow_html=True)


@st.cache_data
def load():
    out = {}
    for name in ["opportunity_table", "segment_matrix", "workarounds"]:
        p = DATA / f"{name}.csv"
        out[name] = pd.read_csv(p) if p.exists() else pd.DataFrame()
    p = DATA / "evidence.jsonl"
    out["evidence"] = pd.DataFrame([json.loads(l) for l in open(p, encoding="utf-8")]) if p.exists() else pd.DataFrame()
    p = DATA / "summary.json"
    out["summary"] = json.load(open(p)) if p.exists() else {}
    return out


d = load()
summ = d["summary"]

st.title("Why wishlisted items on Myntra never get bought")
st.caption("An AI discovery engine that reads app reviews, Reddit threads and YouTube comments, "
           "tags each one against a twelve-blocker taxonomy, and ranks opportunities by "
           "frequency, severity, and whether they can be fixed without spending money.")

tab_opp, tab_seg, tab_evid, tab_live, tab_how = st.tabs(
    ["Opportunity ranking", "Segment cuts", "Evidence and workarounds", "Classify a review live", "How it works"])

with tab_opp:
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Documents read", f"{summ.get('total_docs', 0):,}")
    c2.metric("Relevant to a purchase decision", f"{summ.get('relevant_docs', 0):,}",
              f"{summ.get('relevance_rate', 0):.0%} of total")
    c3.metric("Mention the wishlist itself", f"{summ.get('wishlist_mentioned_docs', 0):,}")
    src = summ.get("sources", {})
    c4.metric("Sources", len(src), ", ".join(src.keys())[:40])

    opp = d["opportunity_table"]
    if not opp.empty:
        left, right = st.columns([3, 2])
        with left:
            fig = px.bar(opp.sort_values("opportunity_score"), x="opportunity_score", y="label",
                         orientation="h", text="mentions",
                         labels={"opportunity_score": "Opportunity score", "label": ""},
                         color="addressable_without_money",
                         color_continuous_scale=["#9DB4C0", "#1F4E79"])
            xmax = float(opp["opportunity_score"].max()) * 1.18
            fig.update_layout(height=520, margin=dict(l=10, r=30, t=10, b=10), coloraxis_showscale=False,
                              font=dict(family="Arial", size=13), xaxis=dict(range=[0, xmax]))
            fig.update_traces(textposition="inside", insidetextanchor="end", textfont=dict(color="white", size=13), cliponaxis=False)
            st.plotly_chart(fig, use_container_width=True)
        with right:
            st.markdown("**How to read this**")
            st.markdown('<div class="note">Score = share of relevant documents × mean severity × '
                        'addressable-without-money weight × 30-day latency weight. '
                        'The first two come from the data. The last two are analyst assumptions, '
                        'shown in the table so you can disagree with them.</div>', unsafe_allow_html=True)
            st.markdown("**Intent behind saving** (where inferable)")
            intents = pd.DataFrame(list(summ.get("intent_distribution", {}).items()), columns=["intent", "docs"])
            if not intents.empty:
                st.dataframe(intents.sort_values("docs", ascending=False), hide_index=True, use_container_width=True)
        st.markdown("**Full opportunity table**")
        show = opp[["rank", "label", "mentions", "share_of_relevant_docs", "mean_severity", "decisive_mentions",
                    "wishlist_co_mentions", "addressable_without_money", "latency_impact", "opportunity_score"]]
        st.dataframe(show, hide_index=True, use_container_width=True)
    else:
        st.info("No data yet. Run generate_sample_corpus.py, classify.py and aggregate.py first.")

with tab_seg:
    seg = d["segment_matrix"]
    if seg.empty:
        st.info("No segment data yet.")
    else:
        field = st.selectbox("Cut by", list(SEGMENT_FIELDS.keys()), index=3)
        sub = seg[(seg.segment_field == field) & (seg.segment_value != "unknown")]
        if sub.empty:
            st.warning("No documents carried an explicit cue for this segment field. "
                       "Expect this to fill in with real data and LLM classification.")
        else:
            piv = sub.pivot(index="blocker", columns="segment_value", values="share").fillna(0)
            piv.index = [BLOCKERS[b]["label"] for b in piv.index]
            fig = px.imshow(piv, text_auto=".0%", aspect="auto",
                            color_continuous_scale=["#FFFFFF", "#1F4E79"],
                            labels={"color": "share of docs"})
            fig.update_layout(height=520, margin=dict(l=10, r=10, t=10, b=10), font=dict(family="Arial", size=12))
            st.plotly_chart(fig, use_container_width=True)
            n = sub.groupby("segment_value")["n_docs"].first()
            st.caption("Documents per segment value: " + ", ".join(f"{k}: {v}" for k, v in n.items()))

with tab_evid:
    ev, wa = d["evidence"], d["workarounds"]
    col_a, col_b = st.columns([3, 2])
    with col_a:
        st.markdown("**Audit trail: what people actually said**")
        if ev.empty:
            st.info("No evidence yet.")
        else:
            pick = st.selectbox("Blocker", list(BLOCKERS.keys()), format_func=lambda k: BLOCKERS[k]["label"])
            rows = ev[ev.blocker == pick].sort_values("severity", ascending=False).head(15)
            for _, r in rows.iterrows():
                st.markdown(f"- *{r['evidence']}*  \n  <span style='color:#666'>{r['source']} · severity {r['severity']} · {r['id']}</span>",
                            unsafe_allow_html=True)
    with col_b:
        st.markdown("**Workarounds users already use**")
        if not wa.empty:
            st.dataframe(wa[wa.type == "workaround"].head(12)[["text", "count"]], hide_index=True, use_container_width=True)
            st.markdown("**What happens outside the app**")
            st.dataframe(wa[wa.type == "outside_app"].head(12)[["text", "count"]], hide_index=True, use_container_width=True)

with tab_live:
    st.markdown("Paste any review, Reddit comment or YouTube comment. The engine applies the same taxonomy it used on the full corpus.")
    sample = ("Saved a Libas kurti in my wishlist two weeks ago. Size chart says L but reviews say it runs small. "
              "I asked my sister on WhatsApp and she said order both M and L. By the time I decided, L was out of stock.")
    text = st.text_area("Text to classify", value=sample, height=140)
    key = os.environ.get("ANTHROPIC_API_KEY")
    if not key:
        try:
            key = st.secrets["ANTHROPIC_API_KEY"]
        except Exception:  # noqa: BLE001
            key = None
    mode = st.radio("Classifier", ["LLM (Claude)", "Keyword heuristic"], horizontal=True,
                    index=0 if key else 1, disabled=not key,
                    help="LLM mode needs ANTHROPIC_API_KEY in Streamlit secrets.")
    if st.button("Classify", type="primary"):
        if mode.startswith("LLM") and key:
            import anthropic
            client = anthropic.Anthropic(api_key=key)
            with st.spinner("Reading"):
                resp = client.messages.create(model=os.environ.get("CLASSIFIER_MODEL", "claude-haiku-4-5-20251001"),
                                              max_tokens=1200, system=SYSTEM_PROMPT,
                                              messages=[{"role": "user", "content": text}])
                raw = _text_of(resp).strip().strip("`").replace("json\n", "", 1)
                try:
                    out = json.loads(raw)
                except json.JSONDecodeError:
                    out = {"raw": raw}
        else:
            out = heuristic(text)
        if out.get("blockers"):
            st.markdown("**Blockers found**")
            for b in out["blockers"]:
                lab = BLOCKERS.get(b["category"], {}).get("label", b["category"])
                st.markdown(f"- **{lab}** (severity {b['severity']}): *{b.get('evidence', '')}*")
        st.markdown(f"Intent: `{out.get('intent_type')}` · Workaround: `{out.get('workaround') or 'none'}` · "
                    f"Outside app: `{out.get('outside_app_behavior') or 'none'}` · Sentiment: `{out.get('sentiment')}`")
        with st.expander("Raw JSON"):
            st.json(out)

with tab_how:
    st.markdown("""
**Pipeline**

1. **Collect.** Four collectors pull public text: Google Play reviews (`google-play-scraper`), App Store reviews
   (Apple RSS), Reddit posts and comments (public JSON endpoints, ten subreddits × ten queries), YouTube comments
   on haul and try-on videos (Data API v3). Everything lands as JSONL with a source tag.
2. **Classify.** Each document goes to Claude with a fixed system prompt that forces JSON: relevance, whether the
   wishlist is mentioned, the user's intent when saving, one or more blockers with a severity score and a verbatim
   evidence quote, the workaround they use, what they do outside the app, and any segment cues. A keyword
   fallback exists for dry runs and is labelled as such.
3. **Aggregate.** Blockers are ranked by an opportunity score that multiplies what the data says
   (frequency, severity) by what the constraint demands (fixable without money, moves a 30-day window).
   Segment cuts and workaround tallies come out of the same pass.
4. **Audit.** Every number links back to quotes, so a reader can challenge any classification.

**Why this is not sentiment analysis.** Sentiment tells you people are unhappy. This tells you *which*
uncertainty stopped a purchase, how often, how badly, for whom, and what they do instead. That is the input
a decomposition needs.

**Known limits.** Reviews over-represent angry users; Reddit over-represents metro English speakers;
segment cues are sparse. Treat the ranking as a prior to test in interviews, not as the answer.
""")
