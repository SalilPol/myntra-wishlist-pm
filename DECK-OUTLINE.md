# Deck outline: NL Myntra (10 slides)

Rules from the brief: no name anywhere, 10 slides max including title, every slide title states
the key message, minimum 14pt in Google Slides or PowerPoint, colour-blind-safe palette, links as
hyperlinks with access open, file under 40 MB, named `NL Myntra`.

Palette suggestion (colour-blind safe, readable on white): ink #1C1B22, slate #5C6370,
accent #D6336C for the one thing per slide that matters, teal #0F7B6C for positive, amber
#B7791F for caution. Never encode meaning in colour alone; label it.

| # | Slide title (the message) | Content | Source file |
|---|---|---|---|
| 1 | Wishlist conversion is a decision-latency problem, not a demand problem | Metric read closely: users, at least one item, 30 days. What that changes. Links to engine and MVP. | `01-metric-decomposition/metric_decomposition.md` |
| 2 | Only one item per user needs to convert, so we work on the top item | Seven-stage decomposition; formula; sensitivity table showing S4 highest per point; price waits excluded by constraint | `metric_decomposition.md`, `wishlist_funnel_model.xlsx` Scenarios |
| 3 | Fit and look block the top item; price waiting sits on third-choice items | Opportunity ranking chart from the engine; top 3 with share and severity; workaround tallies | `02-discovery-engine/data/opportunity_table.csv`, dashboard |
| 4 | How the engine works: collect, classify against 12 blockers, score by what the constraint allows | The required one-slider. Pipeline diagram; scoring formula; what it does that sentiment does not; known limits. Hyperlink to the deployed dashboard | `02-discovery-engine/README.md`, app "How it works" tab |
| 5 | Six shoppers, one pattern: "if someone just told me the size I would buy today" | Segment definition; tag matrix; 6/6 fit, 4/6 look, 4/6 second opinion; two quotes; hyperlink to interview notes | `03-user-research/synthesis.md` |
| 6 | Shoppers already solve this outside Myntra, slowly and at Myntra's expense | Workaround table with cost to user and cost to Myntra; the WhatsApp screenshot as the decision leaving the platform | `synthesis.md`, `04-problem-definition.md` |
| 7 | The wishlist is a parking lot with no exit ramp: no intent, no resolution, no decision moment | Segment, product outcome (S4), root cause, why user value, why business sense, evolution chain in one strip | `04-problem-definition.md` |
| 8 | Wishlist Decide: tag what you meant, get a size you can trust, ask a friend inside, decide by a date | Screenshots of the four moments; how each maps to a stage; "nothing here is monetary". Hyperlink to the live MVP | `05-mvp/README.md`, screenshots of the deployed app |
| 9 | Success is a higher top-item resolution rate with returns flat or down | North star and target; primary metrics; leading indicators; guardrails with thresholds; experiment design in two lines | `06-success-metrics.md` |
| 10 | The feature fails if the verdict is confidently wrong or urgency turns fake | Top 4 risks with mitigation; kill-switch conditions | `07-risks-mitigation.md` |

Build order: slides 8 and 4 need screenshots, so deploy first. Take screenshots at 1920x1080
browser width for crisp images; keep total file size in check by exporting PNG at 2x, not 3x.

Numbers to fill from the workbook: baseline metric (Funnel!B17), combined scenario (Scenarios!B19),
delta (Scenarios!B20), per-point sensitivity ranking (Scenarios column I).
