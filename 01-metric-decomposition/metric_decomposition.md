# Part 2: Breaking down Wishlist to Purchase conversion

Companion workbook: `wishlist_funnel_model.xlsx` (Assumptions, Funnel, Scenarios). All
numbers are illustrative placeholders unless you replace them with real data.

## The metric, read carefully

> Increase the percentage of **users** who purchase **at least one** item from their wishlist
> **within 30 days** of adding it.

Three words change the strategy.

1. **Users, not items.** The denominator is wishlisting users. A user with 40 saved items who
   buys one counts fully. So the job is not "raise wishlist conversion rate", it is "get one
   item per user over the line". That means concentrating effort on each user's single
   highest-intent item, not spreading it across the list.
2. **At least one.** With n intent items each converting with probability p, the chance a user
   converts is 1 - (1 - p)^n. Small increases in p compound across the list. Removing one
   blocker on the top item is worth more than shaving friction across all items.
3. **Within 30 days.** A purchase on day 45 scores zero. This is a decision-latency metric in
   disguise. Anything that lets an item drift (no deadline, no trigger, no state) works against it,
   and anything that trains users to wait (sale cadence) works against it structurally.

## Decomposition

```
% wishlisting users buying >= 1 wishlisted item in 30 days
= S2 Revisit  x  [ 1 - (1 - p)^n ]

where p (item-level) = S1 x S3 x S4 x S5 x S6 x S7
      n              = intent items per user
```

| Stage | Definition | What has to change | Illustrative baseline |
|---|---|---|---|
| **S1 Intent quality** | Share of adds that are real purchase intent, not inspiration | The product knows why the user saved, so it stops treating a mood-board pin like a shortlist | 55% |
| **S2 Revisit** | Share of wishlisting users who reopen the wishlist within 30 days | A reason to come back: something changed for *their* item | 60% |
| **S3 Viability** | Intent items still in stock in the user's size at revisit | Wishlist stops silently decaying | 80% |
| **S4 Resolution** | Viable intent items whose blocking uncertainty gets answered | Fit, look, quality, or second-opinion question gets a credible answer inside the app | 45% |
| **S5 Latency** | Resolved decisions made inside the 30-day window | A decision moment exists; the item does not drift | 75% |
| **S6 Wishlist to cart** | Resolved items added to bag | Buy is one tap from the answer, size pre-selected | 60% |
| **S7 Cart to order** | Bags that become orders | Checkout friction | 65% |

Baseline output of the model: **18.1%** of wishlisting users convert in 30 days.

## Which stage is worth attacking

The Scenarios sheet moves each stage independently and reports metric delta per one
percentage point of lever (column I). Result on the illustrative baseline:

| Stage | Metric delta per 1pp of lever |
|---|---|
| S4 Resolution | 0.33 pp |
| S2 Revisit | 0.30 pp |
| S1 Intent quality | 0.28 pp |
| S6 Wishlist to cart | 0.26 pp |
| S7 Cart to order | 0.24 pp |
| S5 Latency | 0.20 pp |
| S3 Viability | 0.19 pp |

S4 wins for a mathematical reason, not a sentimental one: it has the lowest baseline rate, so
it has the most multiplicative headroom. Every stage in a product of rates is worth the same
per relative point, and the lowest stage gives the most relative movement per absolute point.

Two stages are excluded by the constraint or by scope:

- **Price waits** sit inside S5 (latency). The obvious lever, discounts and price-drop alerts,
  is monetary and off the table. That forces the question the brief actually wants answered:
  what non-monetary reason can a user have to decide now rather than at the next sale?
- **S7 Cart to order** belongs to the checkout team, not Growth.

## Product outcomes chosen

Primary: **S4 Resolution.** Raise the share of a user's top-intent wishlisted item whose
blocking uncertainty is answered inside the app, within 7 days of saving.

Secondary: **S5 Latency**, through a decide-by moment tied to the user's stated reason for
saving, and **S3 Viability**, through honest low-stock and restock signals.

Combined MVP scenario (S4 +10pp, S5 +8pp): metric moves from 18.1% to **23.2%**, about
+5.2pp, which on the illustrative base of 10M wishlisting users is roughly 0.5M additional
converting users a month.

## Segment logic

The model is the same for every segment; the stage rates differ. The discovery engine and
interviews are used to find the segment where **S4 is lowest and most addressable without
money**, because that is where a resolution product moves the metric fastest. See
`../04-problem-definition.md` for the segment chosen and why.

## How this connects to the rest of the work

- The engine's blocker taxonomy maps onto S1 (BOOKMARK_ONLY), S3 (AVAILABILITY),
  S4 (FIT_SIZE, LOOK_STYLE, QUALITY, SOCIAL_VALIDATION, ALTERNATIVES), S5 (PRICE_WAIT,
  OCCASION_TIMING), S2 and S4 (APP_UX). The opportunity score's latency weight is the S5 view.
- The interview guide probes S1 (why saved), S4 (what would have to be true), S5 (when will
  you decide), and workarounds (how users resolve S4 today without us).
- Success metrics in `../06-success-metrics.md` are the S-stage rates measured on the
  treatment group, with return rate as the guardrail against a false S4 (a wrong fit verdict).
