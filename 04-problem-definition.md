# Part 4: Problem definition

## In one sentence

Repeat Myntra shoppers save apparel they want and can afford, then fail to buy it within 30
days because the one question that would close the decision ("will this look right on me, in
this size, for this occasion") cannot be answered inside the app, so they answer it slowly and
expensively outside it, or not at all.

## Target user segment

Women, 24 to 32, metro and tier-1, repeat buyers (3+ orders in 12 months), 15+ wishlisted
items, at least one unbought apparel item at Rs 800 to 2,500 saved in the last 60 days.

Sharpest sub-segment: those who have been burned by a return or a sell-out and have therefore
stopped "just ordering it."

Why this segment and not another:

- Highest wishlist volume per user in the corpus and in interviews (34 to 156 items), so the
  "at least one item" structure of the metric works in our favour: there are many candidates.
- Apparel at this price band is where uncertainty is high enough to block and the ticket is
  high enough that ordering two sizes hurts.
- Fit and look uncertainty are the top two engine blockers and were raised by 6/6 and 4/6
  interviewees respectively as the blocker on their most-wanted item.
- The segment already runs the workaround (WhatsApp screenshots, YouTube hauls, two-size
  orders), which proves intent and shows what they are willing to do.

## Product outcome to influence

**S4 Resolution:** raise the share of a user's top-intent wishlisted item whose blocking
uncertainty (fit, look, or second opinion) is answered inside the app within 7 days of saving.

Secondary: **S5 Latency** (a decide-by moment tied to the user's stated occasion) and
**S3 Viability** (honest low-stock and restock signals so the item is still buyable when the
answer arrives).

## Root cause

The wishlist is a **parking lot with no exit ramp.** Three things are missing:

1. **No intent.** Every save is treated identically, whether it is a shortlist item for next
   week or an inspiration pin for never. The product cannot tell which item to work on.
2. **No resolution.** The data that would answer "will it fit me" already exists on the
   platform (the user's kept and returned sizes by brand, thousands of reviews with size
   feedback, customer photos) but is never assembled into a verdict for this user on this item.
   The size chart and the generic size recommender are not verdicts; interviewees said so.
3. **No decision moment.** Nothing in the product asks the user to decide. Items drift until a
   sale notification or a sell-out forces the issue, and the sale cadence has trained users
   that waiting is rational.

The monetary lever (discounts, price-drop alerts) would paper over all three without fixing
any of them, and it is off the table anyway.

## Existing user workarounds and their cost

| Workaround | Who | What it costs the user | What it costs Myntra |
|---|---|---|---|
| Order two sizes, return one | P1, P2, P5 | Money locked for a week or two, pickup risk | Return logistics, inflated return rate |
| Screenshot to a sister, friend or husband on WhatsApp | P1, P3, P4, P6 | A day or more of waiting for "looks nice" | The decision leaves the platform; zero signal captured |
| YouTube hauls and Instagram customer photos | P1, P3, P5 | 20 to 40 minutes, often fruitless | Nothing captured |
| Read 40+ reviews, lowest-rated first | P3, P5, P6 | Time; contradictory answers | Reviews exist but do not resolve |
| Check Amazon or Ajio | P2, P4 | Time | Leakage |
| Leave it and forget | P1, P2, P4 | Lost item, lost trust in the wishlist | Lost purchase, wishlist decay |

## Why solving it creates meaningful user value

The user gets a credible answer to the question she is already spending hours and money to
answer, faster, and without locking Rs 3,000 in a two-size order. She gets a wishlist that
reflects what she actually means (shortlist vs inspiration), a deadline that matches her life
(the engagement is in three weeks), and a way to bring her sister into the decision without
leaving the app. Nothing here pushes her to buy something she does not want; it helps her
buy the thing she does.

## Why solving it makes business sense

- **Directly attacks the lowest-rate stage.** On the illustrative model, S4 has the highest
  metric sensitivity per point moved. Combined with a decide-by moment (S5), the illustrative
  scenario moves the 30-day metric from 18.1% to 23.2%.
- **Reduces returns rather than adding to them.** The two-size workaround is a return by
  design. A trusted single-size verdict replaces it. Return rate is the guardrail and, done
  right, a co-benefit.
- **Captures a decision that currently happens on WhatsApp.** Every friend vote inside the
  app is a signal Myntra does not have today, and a free, non-monetary reason to come back.
- **Non-monetary by construction.** No margin given away, no training users to wait harder.
- **Uses data Myntra already holds.** Kept and returned sizes by brand, review size feedback,
  and stock levels. No new data collection, no new supply-side dependency for v1.

## How the thinking evolved

```
Business metric
  "% of users buying >= 1 wishlisted item within 30 days"
  Read closely: user-level, one item is enough, 30-day window = latency metric.
        |
        v
Product outcomes (decomposition)
  Seven stages. S4 Resolution has the lowest baseline and highest sensitivity.
  Price waits are monetary and excluded. Checkout is out of scope.
  Hypothesis: the biggest gain is answering the blocking question on the top item.
        |
        v
AI discovery (engine over reviews, Reddit, YouTube)
  Blockers ranked: FIT_SIZE, LOOK_STYLE, AVAILABILITY, SOCIAL_VALIDATION on top after the
  no-money and 30-day weights. Workarounds surface: two-size orders, screenshot to friend,
  YouTube hauls. Segment cues sparse; interviews needed to pick a segment.
        |
        v
Primary research (6 interviews, target segment)
  Confirms fit and look as the top-item blockers for 6/6 and 4/6.
  Upgrades social validation from a category to the main resolution mechanism.
  Shows price waiting is real but attached to third-choice items, not the top item.
  Reveals occasions as free, unstated deadlines. Reveals wishlist decay killing trust.
        |
        v
Problem definition
  The wishlist has no intent, no resolution, no decision moment.
  Fix S4 for the top item, add a decide-by moment (S5), keep the item buyable (S3).
  Segment: repeat women shoppers 24 to 32 with long lists, burned by returns or sell-outs.
```

## What we are explicitly not solving

- Price and sale waiting (monetary, and not the top-item blocker).
- Checkout and payment friction (S7, another team).
- Inspiration-only saves (structurally unconvertible in 30 days; we separate them so they stop
  polluting the shortlist, we do not try to convert them).
- Men's segment in v1 (fit dominates and look matters less; the MVP's look module would be
  wasted effort until the fit module is proven).
