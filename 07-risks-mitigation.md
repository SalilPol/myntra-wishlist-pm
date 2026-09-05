# Part 7: Why this could fail, and what to do about it

Ranked by expected damage, not by likelihood alone.

## 1. The size verdict is confidently wrong

**Why it happens.** Purchase history is thin for most users in most brands. The rule-based
engine falls back to usual size plus brand notes plus review signals, and the LLM writes a
fluent explanation on top. Fluency reads as certainty.

**Damage.** Returns go up, the guardrail trips, and users learn that the verdict is just the old
size chart in a nicer font. Trust lost here is very hard to win back.

**Mitigation.**
- Show confidence as a first-class element, not a footnote (already in the MVP: high, reasonable, low with "thin data").
- Below a confidence threshold, do not give a single size. Say "M or L; here is what would settle it" and offer the friend card or a photo-review filter instead.
- Ship behind the return-rate guardrail with a kill switch. Read size-related return reasons weekly.
- Calibrate: for every confidence tier, measure verdict acceptance and return rate; if "high" does not return less than "medium", the tiers are fake and must be recomputed.
- Never let the LLM change the size. It explains; the deterministic engine decides.

## 2. The intent question adds friction and users stop saving

**Why it happens.** Saving is a one-tap, low-commitment act. Asking why turns it into a form.

**Damage.** Wishlist add rate falls; the denominator shrinks; the feature "improves" the metric by
suppressing saves rather than creating purchases.

**Mitigation.**
- The question is optional, one tap, and can be answered later from the wishlist itself. Untagged saves default to "not sure yet" and still get a verdict.
- A/B the placement: at save vs on first wishlist revisit. Ship whichever protects add rate.
- Guardrail on add rate (max 3% drop) with automatic rollback.

## 3. Low-stock signals slide into fake urgency

**Why it happens.** "Only 3 left" works, and the temptation to widen the definition of "low" is
constant. Once it is not true, it is a manipulation, and a monetary trick by another name.

**Damage.** Regulatory exposure (dark-pattern rules are tightening in India), user trust, and a
constraint violation in spirit.

**Mitigation.**
- Low stock is defined as actual units in the user's size at or below a fixed threshold, audited weekly against inventory, threshold published internally.
- No countdown timers, no "selling fast" without a number, no scarcity on items with healthy stock.
- The decide-by date for non-occasion items is two weeks, not "today".

## 4. The friend vote does not come back

**Why it happens.** The friend is outside the app, the link is one more thing to tap, and the
WhatsApp thread already works well enough for her.

**Damage.** The social-validation module becomes a dead tab; the workaround stays on WhatsApp.

**Mitigation.**
- Make the vote page load in under a second with no login, which the MVP already does.
- Measure vote-return rate within 48 hours as a leading indicator; if under 30%, redesign before scaling.
- Fallback that still helps: even a sent card, unanswered, gives the shopper a decide-by prompt, so the module is not zero-value when the friend is silent.

## 5. The lift is pulled-forward demand, not new demand

**Why it happens.** Some of these users would have bought at the next sale anyway. The feature
moves the purchase inside 30 days without adding an order.

**Damage.** The business metric improves, the business case is overstated, and margin may be
worse if full-price purchases were going to happen at sale price anyway (though that cuts the
other way too: buying now is buying at full price).

**Mitigation.**
- Read the experiment at day 45 and day 60 as well as day 30, and report net orders per user over 90 days, not just the 30-day rate.
- Report full-price share of wishlist-origin orders; this is where the honest upside lives.

## 6. Segment cues in the discovery engine are too thin to trust the segment choice

**Why it happens.** Reviews and comments rarely state age, city or gender. The engine's segment
matrix will be mostly "unknown".

**Damage.** The segment is chosen on interview evidence from six people plus a prior, which is a
thin base for a large rollout.

**Mitigation.**
- Treat the segment as a hypothesis and confirm it with Myntra's own data on day one: wishlist size distribution, return rate by cohort, top-item category by cohort.
- Run the experiment on all wishlisting users but pre-register the target segment as the primary read, so the segment claim is tested rather than assumed.

## 7. Privacy and creepiness of "we know your returns"

**Why it happens.** The verdict quotes the user's own returned items and reasons ("too tight at
bust"). That is her data, but seeing it reflected can feel intrusive.

**Damage.** A share of users disable the feature or feel watched.

**Mitigation.**
- The verdict only ever uses the user's own purchase history and never infers body attributes; no measurements are requested or stored.
- Phrase reasons neutrally ("you returned a Sassafras top in M for fit") and offer a one-tap "don't use my returns for this" control.
- Show the history in a "what Myntra already knows" panel so nothing feels hidden.

## 8. The LLM invents a fact

**Why it happens.** Language models fill gaps.

**Damage.** A fabricated review or stock claim in a purchase decision.

**Mitigation.**
- The LLM receives only structured facts and is instructed to use only them; every claim it can make is traceable to an input field.
- Deterministic verdicts render regardless; the LLM layer is an explanation, not a source.
- Log every LLM output with its input; sample 100 a week for factual audit; any fabrication rate above 1% turns the layer off.
