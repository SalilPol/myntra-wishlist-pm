# Interview synthesis (Part 3)

Segment: women 24 to 32, metro, repeat Myntra buyers, 15+ wishlisted items, at least one
unbought apparel item at Rs 800 to 2,500 saved in the last 60 days.

## Tag matrix (severity 1 to 3, blank = not raised)

| Blocker | P1 | P2 | P3 | P4 | P5 | P6 | Raised by | Mean severity |
|---|---|---|---|---|---|---|---|---|
| FIT_SIZE | 3 | 2 | 2 | 3 | 3 | 2 | 6/6 | 2.5 |
| LOOK_STYLE | 2 | | 3 | 2 | | 3 | 4/6 | 2.5 |
| SOCIAL_VALIDATION | 2 | | 3 | 1 | | 2 | 4/6 | 2.0 |
| PRICE_WAIT | 1 | 2 | 1 | | 2 | 1 | 5/6 | 1.4 |
| OCCASION_TIMING | 1 | 1 | 1 | 2 | | 2 | 5/6 | 1.4 |
| AVAILABILITY | | 3 | | 2 | | | 2/6 | 2.5 |
| RETURN_HASSLE | 2 | 1 | | | 1 | | 3/6 | 1.3 |
| QUALITY | | | 2 | | 1 | 2 | 3/6 | 1.7 |
| APP_UX | | 2 | | | 2 | | 2/6 | 2.0 |
| ALTERNATIVES | | 1 | | 1 | | | 2/6 | 1.0 |
| BOOKMARK_ONLY | (mixed list) | (mixed list) | | | (mixed list) | | 3/6 | n/a |

## What the six conversations say together

**1. Every participant had at least one item she wanted, could afford, and had not bought because of a fit or look question she could not answer inside the app.** P1's co-ord, P2's jeans, P3's top, P4's ethnic set, P5's 501s, P6's dress. In four of six cases the participant said, unprompted, some version of "if someone just told me the size I would buy today." This is S4 (resolution) in the decomposition, and it is the lowest-rate stage.

**2. The wishlist is a mixed bag and the product does not know it.** Five of six described their list as part shortlist, part inspiration board, part sale-wait queue, part gift list. Nothing in the product separates these, so the user has to do triage in her head every time she opens it, and mostly does not. P2: "It is a graveyard." P5: "I never reach inbox zero." This is S1 and S2: intent is never captured, so revisit has no focus.

**3. Users resolve uncertainty outside the app, slowly and expensively.** Workarounds observed:

| Workaround | Participants | Cost to user | Cost to Myntra |
|---|---|---|---|
| Order two sizes, return one | P1, P2, P5 | Money locked for 1 to 2 weeks, return pickup risk | Return logistics, ~40% return rate for P5 |
| Screenshot to sister / friend / husband on WhatsApp | P1, P3, P4, P6 | Wait a day or more for a reply that is often "looks nice" | Decision leaves the platform; no signal captured |
| YouTube haul or Instagram customer photos | P3, P5, P1 | 20 to 40 minutes, often does not find the item | None captured |
| Read 40+ reviews, lowest-rated first | P3, P5, P6 | Time, and reviews contradict | Reviews exist but are not synthesised into a verdict |
| Check Amazon or Ajio for the same item | P2, P4 | Time | Leakage risk |
| Buy one, exchange instead of return | P4, P6 | A second delivery cycle | Exchange logistics |
| Leave it and forget | P1, P2, P4 | Lost item | Lost purchase; wishlist decays |

The WhatsApp screenshot is the most telling. Four of six do it, all said it is slow, and two
(P3, P6) asked for an in-app version without being prompted. The decision is being made off
platform, in a chat thread, and Myntra never sees it.

**4. Price waiting is real but shallower than it looks.** Five of six mentioned waiting for a sale, but only for specific higher-ticket items (P2's Puma, P5's blazer, P1's H&M blazer) and always as the third item, not the first. For the item they actually wanted most, price was not the blocker. This matters for the constraint: we do not need to fight the sale wait to move the metric; we need to close the fit and look question on the top item.

**5. Occasions create a natural deadline that the product ignores.** Five of six had a dated occasion behind at least one save (Diwali, Navratri, engagement, brunch, birthday gift). None had told the app. A stated occasion is a free, non-monetary reason to decide before the date, and a free trigger for restock and low-stock alerts.

**6. Availability decay is a trust killer for the heaviest users.** P2 (118 items) and P4 (87) both described sizes selling out while they deliberated, and both have stopped trusting the wishlist as a result. P2 has started not saving items that show "few left." That is the wishlist actively suppressing intent capture.

## What this changes from the engine's prior

The engine ranked FIT_SIZE first, LOOK_STYLE second, AVAILABILITY and SOCIAL_VALIDATION next.
Interviews confirm FIT_SIZE and LOOK_STYLE as the top-item blockers and upgrade
SOCIAL_VALIDATION from "a category" to "the primary workaround mechanism," which means the
product should build on it rather than replace it. Interviews also show that the blockers are
not independent: the user's real question is "will this look right on *me*," and fit, colour,
fabric and a friend's opinion are all partial answers to that one question.

## Segment decision

Stay with the chosen segment. Within it, the sharpest sub-segment is **the repeat buyer with a
long list who has been burned by a return or a sell-out** (P1, P2, P4, P5). They have the most
intent parked, the strongest reason not to "just order it," and the most to gain from a
verdict they can trust.

## Open questions for the real interviews

- Does the "just tell me the size" wish survive when the answer is "we are 70% sure"? What confidence threshold makes someone act?
- How much does a friend's tap inside the app substitute for the WhatsApp thread? Would the friend actually respond?
- For men in the same age band, does look uncertainty drop and fit dominate entirely? (Would change the MVP's emphasis.)
