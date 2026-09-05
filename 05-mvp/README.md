# Wishlist Decide (Part 5 MVP)

A feature inside Myntra's wishlist that turns a parking lot into a decision queue.

## What it does

1. **Asks what you meant.** One tap per item: buying soon, for an occasion, not sure yet, waiting for a sale, just inspiration. Inspiration and sale-waits are moved out of the shortlist so the shortlist stays a shortlist. (Decomposition stage S1.)
2. **Surfaces the one item worth deciding first.** Priority = intent weight × in-stock-in-your-size × urgency (honest low stock, or your own occasion date) × recency, plus a bonus when the fit verdict is confident. The breakdown is shown, not hidden. (S2, S3.)
3. **Gives a size you can trust, with reasons.** The verdict comes from your own kept and returned sizes in that brand and type, then the brand's known sizing behaviour, then review size feedback, applying at most one adjustment so it never double-counts. Confidence is stated. What the data cannot answer (hem length on your height, inseam) is stated too. (S4.)
4. **Answers the look and quality questions.** Pairings from what you already own, colour-accuracy rate from reviews, fabric sentiment, customer-photo count, and real review snippets. (S4.)
5. **Brings the friend inside.** Generates a share card with a one-tap vote link. The friend sees the item (or two items side by side) and taps Get it or Skip it. Votes land on the item. No WhatsApp screenshot, no day-long wait. (S4, and captures a signal Myntra never sees today.)
6. **Sets a decide-by moment.** Tied to the shopper's stated occasion (a week before, leaving time for an exchange) or to true stock levels, otherwise two weeks. Then Add to bag in the recommended size, Keep with reminder, or Remove. (S5, S6.)

Nothing in the flow is monetary. No coupon, discount, price alert, or countdown-to-sale.

## Optional LLM layer

With `ANTHROPIC_API_KEY` set, Claude writes the fit explanation, look advice, quality line and a
decision prompt from the same structured facts. The system prompt forbids inventing reviews,
stock or history and allows it to recommend not buying. Without a key the app shows the
rule-based verdict. The facts are identical either way; only the prose changes.

## Run locally

```bash
pip install -r requirements.txt
export ANTHROPIC_API_KEY=sk-ant-...   # optional
streamlit run app.py
```

## Deploy (public link for the deliverable)

1. Push the repository to GitHub.
2. share.streamlit.io > New app > repo, branch `main`, main file `05-mvp/app.py`.
3. Secrets (optional): `ANTHROPIC_API_KEY = "sk-ant-..."`.
4. After deploy, open the app, go to Ask a friend, paste the public URL into "Your app link"
   so the vote links resolve. Or hard-code it in `engine.share_card` default.

## What a tester should try

- Change the Vero Moda shirt from Inspiration to Buying soon and watch it enter the shortlist with a size-down verdict.
- Change the Sassafras co-ord to Waiting for a sale and watch the Global Desi dress take the top slot because of the engagement date.
- Open the vote link in another tab, vote, come back: the vote count appears on the item.
- Add the top item to bag: it moves to Decided and the next item takes its place.

## Files

```
app.py               Streamlit UI, friend vote view, session state
engine.py            priority scoring, fit and look verdicts, decide-by logic, share card, optional LLM explanation
data/catalog.json    8 illustrative products with sizes, stock, review stats
data/user_profile.json  illustrative shopper: fit history by brand, wardrobe, occasions
data/votes.json      created at runtime by friend votes
```

## What is deliberately not built

- Real Myntra catalogue or images (illustrative products, colour swatches instead of photos).
- Push notifications (the decide-by date is shown; sending it is a platform integration).
- Body-measurement input (the verdict uses purchase history so the shopper never has to type measurements).
- Men's flows (fit dominates, look matters less; prove the fit module first).
