"""
Wishlist Decide: an MVP feature for Myntra's wishlist.

Turns the wishlist from a parking lot into a decision queue:
  1. Ask what the shopper meant by each save (intent).
  2. Surface the one item worth deciding first.
  3. Answer the blocking question (fit, look, quality) from data the platform already holds.
  4. Bring a friend's vote inside the app instead of a WhatsApp screenshot.
  5. Set a decide-by moment tied to the shopper's own occasion or to honest stock levels.

No coupons, no discounts, no price-drop alerts.

Run:     streamlit run app.py
Deploy:  Streamlit Community Cloud. Optional secret ANTHROPIC_API_KEY turns on written explanations.
"""
import json
import os
from datetime import date
from pathlib import Path

import streamlit as st

import engine as E

ROOT = Path(__file__).parent
CATALOG = json.load(open(ROOT / "data" / "catalog.json"))
PROFILE = json.load(open(ROOT / "data" / "user_profile.json"))
VOTES = ROOT / "data" / "votes.json"
BY_ID = {c["id"]: c for c in CATALOG}

st.set_page_config(page_title="Wishlist Decide", page_icon="✓", layout="wide")

st.markdown("""
<style>
  .block-container {padding-top: 1.2rem; max-width: 1120px;}
  :root {--ink:#1C1B22; --accent:#D6336C; --slate:#5C6370; --ok:#0F7B6C; --warn:#B7791F; --panel:#F7F5F8;}
  h1 {font-weight: 700; letter-spacing: -0.02em; color: var(--ink);}
  .card {border:1px solid #E6E3E9; border-radius: 10px; padding: 10px 12px 8px; background:#fff; min-height: 150px;}
  .swatch {height: 64px; border-radius: 8px; display:flex; align-items:center; justify-content:center; font-size: 30px; margin-bottom: 8px;}
  .brand {font-size: 12px; color: var(--slate); text-transform: none;}
  .name {font-weight: 600; color: var(--ink); line-height: 1.2;}
  .price {font-size: 13px; color: var(--ink); margin-top: 2px;}
  .verdict {background: var(--ink); color:#fff; border-radius: 12px; padding: 18px 22px; margin: 4px 0 10px;}
  .verdict .size {font-size: 44px; font-weight: 700; line-height: 1; letter-spacing:-0.02em;}
  .verdict .conf {font-size: 14px; opacity: .85; margin-top: 4px;}
  .verdict .why {font-size: 14px; margin-top: 12px; opacity: .95;}
  .pill {display:inline-block; padding: 2px 9px; border-radius: 999px; font-size: 12px; margin-right: 6px;}
  .pill-ok {background:#E3F3F0; color: var(--ok);}
  .pill-warn {background:#FFF3DA; color: var(--warn);}
  .pill-acc {background:#FCE4EC; color: var(--accent);}
  .muted {color: var(--slate); font-size: 13px;}
  .panel {background: var(--panel); border-radius: 10px; padding: 12px 14px;}
  .stButton>button[kind="primary"] {background: var(--accent); border-color: var(--accent);}
</style>
""", unsafe_allow_html=True)


def api_key():
    k = os.environ.get("ANTHROPIC_API_KEY")
    if k:
        return k
    try:
        return st.secrets["ANTHROPIC_API_KEY"]
    except Exception:  # noqa: BLE001
        return None


def load_votes():
    try:
        return json.load(open(VOTES))
    except Exception:  # noqa: BLE001
        return {}


def save_vote(item_id, vote):
    v = load_votes()
    v.setdefault(item_id, []).append({"vote": vote, "at": date.today().isoformat()})
    try:
        json.dump(v, open(VOTES, "w"))
    except Exception:  # noqa: BLE001
        pass
    st.session_state.setdefault("votes", {}).setdefault(item_id, []).append(vote)


def item_card(it, show_price=True):
    st.markdown(f"""
<div class="card">
  <div class="swatch" style="background:{it['hex']}">{it['emoji']}</div>
  <div class="brand">{it['brand']}</div>
  <div class="name">{it['name']}</div>
  <div class="price">{'Rs ' + format(it['price'], ',') if show_price else ''} <span class="muted">· {it['colour']}</span></div>
</div>""", unsafe_allow_html=True)


# ------------------------------------------------------------------ friend vote view
q = st.query_params
if "vote" in q and q["vote"] in BY_ID:
    it = BY_ID[q["vote"]]
    other = BY_ID.get(q.get("vs", ""), None)
    st.markdown(f"## {PROFILE['name']} wants your opinion")
    st.caption("Ten seconds. No account needed.")
    cols = st.columns(2 if other else 1)
    with cols[0]:
        item_card(it)
        st.markdown(f"<div class='muted'>Size {E.fit_verdict(it, PROFILE)['size']} · {it['material']}</div>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        if c1.button("Get it", key="yes_a", type="primary", use_container_width=True):
            save_vote(it["id"], "yes"); st.success("Sent. Priya will see your vote on the item.")
        if c2.button("Skip it", key="no_a", use_container_width=True):
            save_vote(it["id"], "no"); st.success("Sent.")
    if other:
        with cols[1]:
            item_card(other)
            st.markdown(f"<div class='muted'>Size {E.fit_verdict(other, PROFILE)['size']} · {other['material']}</div>", unsafe_allow_html=True)
            c1, c2 = st.columns(2)
            if c1.button("Get this one instead", key="yes_b", type="primary", use_container_width=True):
                save_vote(other["id"], "yes"); save_vote(it["id"], "no"); st.success("Sent.")
            if c2.button("Neither", key="no_b", use_container_width=True):
                save_vote(other["id"], "no"); save_vote(it["id"], "no"); st.success("Sent.")
    st.markdown("---")
    st.markdown("<span class='muted'>This is a prototype of a Myntra wishlist feature. Nothing here is a real listing.</span>", unsafe_allow_html=True)
    st.stop()

# ------------------------------------------------------------------ state
if "intent" not in st.session_state:
    st.session_state.intent = {c["id"]: c["default_intent"] for c in CATALOG}
    st.session_state.decisions = {}   # item_id -> {"action":..., "size":..., "date":...}
    st.session_state.selected = None
    st.session_state.votes = {}
    st.session_state.llm = {}

# ------------------------------------------------------------------ sidebar
with st.sidebar:
    st.markdown(f"**{PROFILE['name']}**  \n<span class='muted'>Repeat shopper · usual size {PROFILE['usual_top_size']} · {PROFILE['height_cm']} cm</span>", unsafe_allow_html=True)
    st.markdown("**What Myntra already knows**")
    st.caption("Kept and returned sizes, by brand. This is the data the size verdicts run on.")
    for h in PROFILE["fit_history"]:
        tag = "✓ kept" if h["outcome"] == "kept" else f"✗ returned ({h.get('reason', '')})"
        st.markdown(f"<span class='muted'>{h['brand']} {h['sub']} · {h['size']} · {tag}</span>", unsafe_allow_html=True)
    st.markdown("**Occasions**")
    for o in PROFILE["occasions"]:
        st.markdown(f"<span class='muted'>{o['name']} · {o['date']} · in {E.days_to(o['date'])} days</span>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("**Written explanations** " + ("<span class='pill pill-ok'>on</span>" if api_key() else "<span class='pill pill-warn'>off</span>"), unsafe_allow_html=True)
    st.caption("With an API key the app writes the explanation from the same facts. Without one it shows the rule-based verdict. Facts are identical either way.")
    if st.button("Reset demo"):
        for k in list(st.session_state.keys()):
            del st.session_state[k]
        st.rerun()

# ------------------------------------------------------------------ header
st.markdown("# Your wishlist, sorted by what you meant")
st.markdown("<span class='muted'>Eight saved items. Tell us why you saved each one and we will show you the one worth deciding first, "
            "with a size you can trust, what to wear it with, and a way to ask a friend without leaving.</span>", unsafe_allow_html=True)

# ------------------------------------------------------------------ step 1: intent
st.markdown("### 1. What did you mean when you saved these?")
cols = st.columns(4)
for i, it in enumerate(CATALOG):
    with cols[i % 4]:
        item_card(it)
        st.session_state.intent[it["id"]] = st.selectbox(
            "Why did you save it?", list(E.INTENT_LABELS.keys()),
            format_func=lambda k: E.INTENT_LABELS[k],
            index=list(E.INTENT_LABELS.keys()).index(st.session_state.intent[it["id"]]),
            key=f"intent_{it['id']}", label_visibility="collapsed")

# ------------------------------------------------------------------ step 2: triage
ranked = []
for it in CATALOG:
    if it["id"] in st.session_state.decisions:
        continue
    p = E.priority(it, st.session_state.intent[it["id"]], PROFILE)
    ranked.append((p["score"], it, p))
ranked.sort(key=lambda x: -x[0])
shortlist = [r for r in ranked if st.session_state.intent[r[1]["id"]] in ("buy_soon", "occasion", "unsure")]
parked = [r for r in ranked if st.session_state.intent[r[1]["id"]] == "sale_wait"]
inspo = [r for r in ranked if st.session_state.intent[r[1]["id"]] == "inspiration"]

st.markdown("### 2. Decide this one first")
if not shortlist:
    st.info("Nothing on the shortlist. Everything is parked for a sale, inspiration, or already decided.")
else:
    if st.session_state.selected not in {r[1]["id"] for r in shortlist}:
        st.session_state.selected = shortlist[0][1]["id"]
    top = next(r for r in shortlist if r[1]["id"] == st.session_state.selected)
    score, it, p = top
    fit = p["fit"]
    look = E.look_verdict(it, PROFILE)
    dby = E.decide_by(it, st.session_state.intent[it["id"]], PROFILE)

    left, right = st.columns([1, 2.2])
    with left:
        item_card(it)
        st.markdown(f"<div class='muted' style='margin-top:6px'>Why first: {p['breakdown']['intent']} · {p['breakdown']['urgency']} · fit confidence {fit['confidence']}</div>", unsafe_allow_html=True)
        if len(shortlist) > 1:
            st.markdown("<div class='muted' style='margin-top:10px'>Next in line</div>", unsafe_allow_html=True)
            for s, o, _ in shortlist[1:4]:
                if st.button(f"{o['brand']} {o['name']}", key=f"pick_{o['id']}", use_container_width=True):
                    st.session_state.selected = o["id"]; st.rerun()
    with right:
        stock_pill = (f"<span class='pill pill-warn'>only {fit['stock']} left in {fit['size']}</span>" if 0 < fit["stock"] <= 3
                      else f"<span class='pill pill-ok'>in stock in {fit['size']}</span>" if fit["stock"]
                      else f"<span class='pill pill-warn'>{fit['size']} sold out" + (f", {fit['alternative']} available" if fit["alternative"] else "") + "</span>")
        conf_word = {"high": "High confidence", "medium": "Reasonable confidence", "low": "Low confidence, thin data"}[fit["confidence"]]
        st.markdown(f"""
<div class='verdict'>
  <div class='size'>Size {fit['size']}</div>
  <div class='conf'>{conf_word} {stock_pill}</div>
  <div class='why'>{'<br>'.join(fit['reasons'])}</div>
</div>""", unsafe_allow_html=True)

        key = api_key()
        llm = None
        if key:
            if it["id"] not in st.session_state.llm:
                with st.spinner("Writing it up from your history and the reviews"):
                    st.session_state.llm[it["id"]] = E.llm_explain(it, st.session_state.intent[it["id"]], PROFILE, fit, look, key)
            llm = st.session_state.llm[it["id"]]
            if llm and "error" in llm:
                st.caption(f"Explanation unavailable ({llm['error'][:80]}). Showing rule-based verdict.")
                llm = None

        t_fit, t_look, t_qual, t_friend, t_decide = st.tabs(["Fit", "Look", "Quality", "Ask a friend", "Decide"])
        with t_fit:
            if llm:
                st.markdown(llm.get("fit_explanation", ""))
            for u in fit["unknown"] + (llm.get("still_unknown", []) if llm else []):
                st.markdown(f"<span class='pill pill-warn'>still unknown</span> {u}", unsafe_allow_html=True)
            if not fit["unknown"] and not llm:
                st.markdown("<span class='muted'>Nothing else the data cannot answer for this item.</span>", unsafe_allow_html=True)
        with t_look:
            if llm:
                st.markdown(llm.get("look_advice", ""))
            else:
                st.markdown("**Goes with what you own:** " + ", ".join(look["pairings"]) if look["pairings"] else "No obvious pairings in your recent purchases.")
            st.markdown(look["colour_note"])
            st.markdown(f"<span class='muted'>{look['photo_reviews']} reviews include customer photos.</span>", unsafe_allow_html=True)
            with st.expander("What buyers said"):
                for sn in look["snippets"]:
                    st.markdown(f"- {sn}")
        with t_qual:
            st.markdown(llm.get("quality_line", E.quality_note(it)) if llm else E.quality_note(it))
            st.markdown(f"<span class='muted'>Average rating {it['reviews']['avg']} from {it['reviews']['count']:,} reviews. "
                        f"{'Returnable' if it['returnable'] else 'Not returnable'}.</span>", unsafe_allow_html=True)
        with t_friend:
            st.markdown("Instead of a screenshot on WhatsApp, send a card your friend can answer in one tap. Her vote lands on this item.")
            others = [o for _, o, _ in shortlist if o["id"] != it["id"]]
            vs = st.selectbox("Compare with (optional)", [None] + others, format_func=lambda o: "Just this one" if o is None else f"{o['brand']} {o['name']}")
            base_url = st.text_input("Your app link", value="https://wishlist-decide.streamlit.app", help="After deploying, paste the public URL here so the vote link works.")
            text, link = E.share_card(it, fit, base_url, vs)
            st.code(text, language=None)
            st.markdown(f"[Open the vote page as your friend would]({link})")
            votes = st.session_state.votes.get(it["id"], []) + [v["vote"] for v in load_votes().get(it["id"], [])]
            if votes:
                yes = votes.count("yes"); no = votes.count("no")
                st.markdown(f"<span class='pill pill-acc'>{yes} say get it</span> <span class='pill'>{no} say skip</span>", unsafe_allow_html=True)
        with t_decide:
            if llm:
                st.markdown(f"**{llm.get('decision_prompt', '')}**")
            st.markdown(f"**Decide by {dby['date']}.** {dby['why']}")
            size_choice = fit["size"] if fit["stock"] else (fit["alternative"] or fit["size"])
            c1, c2, c3 = st.columns(3)
            if c1.button(f"Add to bag in {size_choice}", type="primary", use_container_width=True, disabled=not (fit["stock"] or fit["alternative"])):
                st.session_state.decisions[it["id"]] = {"action": "bag", "size": size_choice}; st.rerun()
            if c2.button(f"Keep, remind me {dby['date']}", use_container_width=True):
                st.session_state.decisions[it["id"]] = {"action": "keep", "date": dby["date"]}; st.rerun()
            if c3.button("Remove from wishlist", use_container_width=True):
                st.session_state.decisions[it["id"]] = {"action": "remove"}; st.rerun()

# ------------------------------------------------------------------ step 3: the rest
st.markdown("### 3. The rest of your list")
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown(f"**Shortlist** <span class='muted'>{len(shortlist)}</span>", unsafe_allow_html=True)
    for s, o, pp in shortlist:
        st.markdown(f"<span class='muted'>{o['brand']} {o['name']} · size {pp['fit']['size']} · {pp['breakdown']['urgency']}</span>", unsafe_allow_html=True)
with c2:
    st.markdown(f"**Waiting for a sale** <span class='muted'>{len(parked)}</span>", unsafe_allow_html=True)
    st.markdown("<span class='muted'>We will not nag you about these. We will tell you if your size gets low.</span>", unsafe_allow_html=True)
    for s, o, pp in parked:
        st.markdown(f"<span class='muted'>{o['brand']} {o['name']} · {pp['breakdown']['urgency']}</span>", unsafe_allow_html=True)
with c3:
    st.markdown(f"**Inspiration** <span class='muted'>{len(inspo)}</span>", unsafe_allow_html=True)
    st.markdown("<span class='muted'>Kept out of the shortlist so it stays a shortlist.</span>", unsafe_allow_html=True)
    for s, o, pp in inspo:
        st.markdown(f"<span class='muted'>{o['brand']} {o['name']}</span>", unsafe_allow_html=True)

if st.session_state.decisions:
    st.markdown("### Decided")
    n_short = len([c for c in CATALOG if st.session_state.intent[c["id"]] in ("buy_soon", "occasion", "unsure")])
    n_done = len(st.session_state.decisions)
    st.markdown(f"<span class='pill pill-ok'>{n_done} decided</span> <span class='muted'>of {n_short} on your shortlist</span>", unsafe_allow_html=True)
    for iid, d in st.session_state.decisions.items():
        o = BY_ID[iid]
        what = {"bag": f"added to bag in {d.get('size')}", "keep": f"kept, reminder on {d.get('date')}", "remove": "removed"}[d["action"]]
        st.markdown(f"<span class='muted'>{o['brand']} {o['name']} · {what}</span>", unsafe_allow_html=True)

st.markdown("---")
st.markdown("<span class='muted'>Prototype. Products, reviews and history are illustrative. No discounts, coupons or price alerts are used anywhere in this flow.</span>", unsafe_allow_html=True)
