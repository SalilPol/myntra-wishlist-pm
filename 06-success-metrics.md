# Part 6: Defining success

## Start with the business metric

**North star: % of wishlisting users who buy at least one wishlisted item within 30 days of adding it.**
Measured on a randomised holdout: users exposed to Wishlist Decide vs users with the current
wishlist. Cohort by the week of first wishlist add so the 30-day window is clean. Read at day 30
and day 45 (the day-45 read tells you whether the feature pulled purchases forward or created them).

Illustrative baseline 18.1%; MVP scenario target 23.2% (see `01-metric-decomposition`).
Real baseline comes from Myntra's data warehouse on day one.

## Metrics the solution directly moves (primary)

| Metric | Definition | Why it is the right proxy |
|---|---|---|
| **Top-item resolution rate (S4)** | Share of shortlisted top items where the shopper opened the verdict and took any decide action (bag, keep-with-date, remove) within 7 days of saving | This is the mechanism. If it does not move, nothing downstream will. Includes Remove on purpose: a clean removal is a resolved decision, and a shrinking, truer shortlist is a healthy sign |
| **Top-item bag rate** | Share of top items added to bag within 14 days of saving, in the recommended size | Converts resolution into the funnel step the business metric needs |
| **Save-to-decision latency** | Median days from save to first decide action on the top item | The 30-day window is a latency metric in disguise. Target: cut the median in half |
| **Wishlist-origin order rate** | Orders containing at least one item that was on the wishlist at least 24 hours before purchase, per wishlisting user | Guards against the feature simply cannibalising direct purchases |

## Leading indicators (read in week one, before conversion is visible)

| Indicator | Definition | What it tells you |
|---|---|---|
| Intent tag completion | Share of new saves that receive an intent tag within the session | Whether users accept the one-tap ask. Below 40% and the shortlist has no signal to work with |
| Shortlist share | Share of tagged saves marked buying soon, occasion, or unsure | Sizes the addressable pool. Also a truth check on S1 |
| Verdict open rate | Share of shortlist users who open the Decide-first panel | Whether the surfacing works |
| Verdict acceptance | Share of bag adds that use the recommended size (vs a different size) | Whether users trust the verdict. Below 60% and the fit model needs work before scaling |
| Friend-card sends and vote returns | Sends per shortlist user; share of sends that get a vote back within 48 hours | Whether the in-app version beats WhatsApp. Vote-return rate is the number that matters |
| Reminder set rate | Share of top items where the user chooses Keep with a date | Whether the decide-by moment is accepted rather than dismissed |

## Guardrails (the feature is stopped or reworked if these move the wrong way)

| Guardrail | Threshold | Why |
|---|---|---|
| **Return rate on wishlist-origin orders** | Must not exceed control by more than 1 percentage point; target is a reduction | A confident wrong size verdict is worse than no verdict. This is the single most important guardrail |
| **Size-related return reasons** | Share of returns citing size, treatment vs control | Isolates the fit model's error from other return causes |
| **Wishlist add rate** | Adds per active user must not fall by more than 3% | The intent question must not add enough friction to suppress saving |
| **Notification opt-out** | Reminder opt-outs must stay under control levels | The decide-by reminder must not feel like nagging |
| **Low-stock accuracy** | Every low-stock label audited against actual inventory; zero tolerance for fabricated scarcity | False urgency is a monetary trick in disguise and destroys trust |
| **Friend-link abuse** | Reports per 1,000 sends | The vote page is public; watch for spam |
| **Customer support contacts about size** | Per 1,000 wishlist-origin orders | A second read on verdict quality |

## Counter-metric to watch, not guard

**Wishlist removal rate** will rise. That is intended: the feature asks users to prune
inspiration and to remove resolved items. Read it alongside add rate and shortlist share. Rising
removals with stable adds is health; rising removals with falling adds is the intent question
backfiring.

## How to read the experiment

- Minimum detectable effect on the north star: 1.5 pp at 80% power; with an illustrative
  base rate of 18% that needs roughly 15,000 wishlisting users per arm, which a large app
  reaches in days. Run 5 weeks: 4 weeks of enrolment, 30-day window on the last cohort.
- Report the north star by segment (target segment first), by intent type, and by fit
  confidence tier. If high-confidence verdicts convert and low-confidence ones do not, the
  product decision is to hide low-confidence verdicts, not to scale the feature as is.
- Day-45 read: if the day-30 lift disappears by day 45, the feature is pulling purchases
  forward, which still meets the metric but is a weaker business case than net-new orders.
  Say so honestly.
