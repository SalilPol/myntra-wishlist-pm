# Deploying this project: a guide for someone who does not code

You will put the project on GitHub (a place that stores project files online), then tell
Streamlit (a free service that runs the apps) to run two of those files as websites.
No typing of commands is needed. Everything is clicks and copy-paste in a web browser.
Use Google Chrome. Total time: 30 to 45 minutes, most of it waiting.

You will end up with two public links:
- Discovery engine: `https://wishlist-discovery.streamlit.app` (or similar)
- MVP: `https://wishlist-decide.streamlit.app` (or similar)

---

## Part A: Get the files ready (2 minutes)

1. Find `myntra-wishlist-pm.zip` in your Downloads folder.
2. Double-click it. A folder called `myntra-wishlist-pm` appears next to it.
3. Open that folder. You should see folders named `01-metric-decomposition`, `02-discovery-engine`,
   `03-user-research`, `05-mvp`, and files like `README.md`, `DEPLOY.md`, `requirements.txt`.
   Leave this window open; you will drag from it later.

---

## Part B: Create a GitHub account and an empty project (5 minutes)

1. Go to **github.com** and click **Sign up**. Use your normal email. Verify the email when asked.
2. Once logged in, click the **+** icon at the top right, then **New repository**.
3. Fill in:
   - Repository name: `myntra-wishlist-pm`
   - Description: leave blank
   - Choose **Public**
   - Do **not** tick "Add a README file". Leave every box unticked.
4. Click the green **Create repository** button.
5. You land on a page with setup instructions. Ignore all the code on it.

---

## Part C: Upload the project to GitHub (5 minutes)

1. On that same page, find the sentence "Get started by creating a new file or **uploading an existing file**". Click **uploading an existing file**.
2. You see a large dotted box that says "Drag files here to add them to your repository".
3. Go to the folder window from Part A. Select **everything inside** the `myntra-wishlist-pm` folder
   (click once inside the folder, then press Ctrl+A on Windows or Cmd+A on Mac).
   You are selecting the contents, not the outer folder itself.
4. Drag the selection onto the dotted box in Chrome and let go.
5. Wait. A list of files appears below the box. It should grow to about 42 files, with names like
   `02-discovery-engine/app.py` and `05-mvp/engine.py`. If the list shows only a handful of files
   with no folder names, the folders did not come through: refresh the page and try again, dragging
   more slowly, and make sure you are in Chrome.
6. Scroll to the bottom. In the box under "Commit changes" leave the text as it is.
7. Click the green **Commit changes** button.
8. After a few seconds you land on the repository home page. Check: you can see folders
   `01-metric-decomposition`, `02-discovery-engine`, `03-user-research`, `05-mvp` and the files.
   If yes, the upload worked.

---

## Part D: Get an Anthropic API key (5 minutes, optional but recommended)

This key lets the apps use Claude to write explanations and classify reviews. Without it the MVP
still works with rule-based verdicts, but the engine's "Classify a review live" tab will not.

1. Go to **console.anthropic.com** and sign up.
2. Anthropic requires prepaid credit. Click **Billing** (or Plans and billing), add a card, and buy
   the minimum, 5 US dollars. That covers this whole project many times over.
3. Click **API keys** in the left menu, then **Create Key**. Name it `streamlit`.
4. A long code starting with `sk-ant-` appears **once**. Click copy, paste it into a note on your
   phone or a text file. You will need it twice. Do not share it with anyone.

---

## Part E: Deploy the discovery engine (10 minutes)

1. Go to **share.streamlit.io**. Click **Continue with GitHub**. Click **Authorize** when GitHub asks.
2. On the Streamlit page click **Create app** (top right). If it asks "Do you already have an app?",
   choose the option to deploy from GitHub.
3. Fill in the form:
   - Repository: click the box and pick `<your-username>/myntra-wishlist-pm`
   - Branch: `main`
   - Main file path: type exactly `02-discovery-engine/app.py`
   - App URL: type `wishlist-discovery`. If it says the name is taken, add your initials, like `wishlist-discovery-sk`.
4. Click **Advanced settings**.
   - Python version: leave as is.
   - Secrets: in the big text box, paste this one line, replacing the dots with your key from Part D
     (keep the quotation marks):
     ```
     ANTHROPIC_API_KEY = "sk-ant-..."
     ```
   - Click **Save**.
5. Click **Deploy**.
6. A screen says your app is being built, with a log scrolling on the right. This takes 2 to 5
   minutes. When it finishes, the app appears.
7. Check it works: you should see the title "Why wishlisted items on Myntra never get bought"
   and a bar chart. Click the tab **Classify a review live**, then the **Classify** button.
   If a list of blockers appears under the text box, the key works.
8. Copy the address from the browser bar. That is your Part 1 link. Save it in your note.

---

## Part F: Deploy the MVP (10 minutes)

1. Back on **share.streamlit.io**, click **Create app** again.
2. Fill in:
   - Repository: same one
   - Branch: `main`
   - Main file path: type exactly `05-mvp/app.py`
   - App URL: type `wishlist-decide`. If taken, add your initials, and note the name you used.
3. Advanced settings > Secrets: paste the same `ANTHROPIC_API_KEY = "sk-ant-..."` line. Save.
4. Click **Deploy**. Wait 2 to 5 minutes.
5. Check it works: you should see "Your wishlist, sorted by what you meant", eight product cards,
   and a dark box saying "Size M". Copy the address. That is your Part 5 link. Save it.

---

## Part G: Make the friend-vote link work (5 minutes)

The MVP's "Ask a friend" tab builds a link your friend taps to vote. It is preset to
`https://wishlist-decide.streamlit.app`. If your app got exactly that address, skip to step 5.
If your address is different (for example `wishlist-decide-sk`), do this:

1. On GitHub, open your repository, click the `05-mvp` folder, then click `app.py`.
2. Click the **pencil icon** (Edit this file) at the top right of the file view.
3. Press Ctrl+F (Cmd+F on Mac) and search for `wishlist-decide.streamlit.app`.
   Change it to your real address, for example `wishlist-decide-sk.streamlit.app`. Change nothing else.
4. Click the green **Commit changes** button, then **Commit changes** again in the pop-up.
   Streamlit notices the change and rebuilds the app on its own in about a minute.
5. Test the loop: open your MVP, click the **Ask a friend** tab, click the link
   "Open the vote page as your friend would". A new tab opens showing the item with **Get it**
   and **Skip it** buttons. Click **Get it**. Go back to the first tab and click the browser's
   refresh button, then the Ask a friend tab again. You should see "1 say get it".

---

## Part H: Before you submit (2 minutes)

- Open both links in a private or incognito window (Ctrl+Shift+N in Chrome). They must load
  without asking you to log in.
- Free Streamlit apps go to sleep after a few days without visitors. Open both links on the
  morning you submit so they are awake; a sleeping app shows a "wake up" button that takes
  30 seconds, which is fine but not ideal for an assessor.
- Put both links in the deck as clickable hyperlinks.

---

## If something goes wrong

| What you see | What to do |
|---|---|
| Upload shows only a few files, no folders | Use Chrome. Drag the contents (Ctrl+A inside the folder), not the folder itself. |
| Streamlit build fails with red text mentioning "requirements" or a package name | Check the Main file path is typed exactly: `02-discovery-engine/app.py` or `05-mvp/app.py`. Fix it in the app's Settings and click Reboot. |
| Engine says "ANTHROPIC_API_KEY not set" or the Classify button does nothing useful | The secret was not saved. In share.streamlit.io, click the three dots next to your app > Settings > Secrets. Paste the line again, Save, then Reboot app. |
| App shows "This app has gone to sleep" | Click the wake-up button. Wait 30 seconds. |
| You changed a file on GitHub but the app looks the same | Wait one minute, then refresh. If still the same: three dots > Reboot app. |
| App name already taken | Add your initials or a number to the URL. Remember to update the vote link in Part G. |
| You lost the API key | Make a new one in console.anthropic.com > API keys, and paste it into both apps' Secrets. |

If you get stuck, copy the red text from the Streamlit log and paste it into our chat.
