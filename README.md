# Hindi Personal Finance / Govt Scheme Site — Auto-Publishing Setup

A free, automated pipeline: Sarvam AI writes a Hindi article every day, GitHub
Actions commits it, and the static site rebuilds and deploys itself — no
manual publishing needed once it's running.

## What's in this folder
```
config.toml                          Hugo site config
content/posts/                       generated articles land here
content/about.md                     About page (required by AdSense)
content/privacy-policy.md            Privacy policy (required by AdSense)
data/topics.json                     rotating list of article topics
data/used_topics.json                auto-created; tracks which topics were used
scripts/generate_post.py             calls Sarvam API, writes a new post
.github/workflows/generate-and-deploy.yml   daily automation
```

## One-time setup (about 20–30 minutes)

1. **Create a GitHub account** (if you don't have one) and a new **public**
   repository, e.g. `hindi-finance-site`.

2. **Push this folder** to that repo:
   ```bash
   cd hindi-finance-site
   git init
   git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPO.git
   git add .
   git commit -m "Initial setup"
   git branch -M main
   git push -u origin main
   ```

3. **Add the PaperMod theme** (free Hugo theme, good for blogs):
   ```bash
   git submodule add https://github.com/adityatelange/hugo-PaperMod themes/PaperMod
   git commit -m "Add theme"
   git push
   ```

4. **Edit `config.toml`**: replace `baseURL` with your real GitHub Pages URL
   (`https://YOUR-USERNAME.github.io/YOUR-REPO/`) and change the site title.

5. **Get a Sarvam API key**: sign up at dashboard.sarvam.ai (this is where
   your free credits live), copy your API key.

6. **Add the key as a GitHub secret**:
   Repo → Settings → Secrets and variables → Actions → New repository secret
   Name: `SARVAM_API_KEY`  Value: (paste your key)

7. **Enable GitHub Pages via Actions**:
   Repo → Settings → Pages → Source → select "GitHub Actions"

8. **Run the workflow once manually** to test it:
   Repo → Actions tab → "Generate post and deploy site" → Run workflow

   Check that a new file appeared in `content/posts/` and that your site is
   live at the GitHub Pages URL.

That's it — from here, it runs daily on its own (the cron schedule in the
workflow file), generating one new article and redeploying automatically.

## Before applying to AdSense
- Let it run for 2–3 weeks so you have 15–20 posts.
- Replace the placeholder email in `about.md` and `privacy-policy.md`.
- Skim a handful of generated posts for quality/accuracy — Sarvam is good,
  but for finance content it's worth a quick human check.
- Apply at adsense.google.com with your live site URL.
- Once approved, paste the AdSense script snippet into
  `themes/PaperMod/layouts/partials/head.html` (or use a Hugo partial
  override) so it applies to every page automatically.

## Adjusting the schedule / topics
- Change the `cron` line in the workflow file to post more or less often
  (e.g. `0 3 * * 1,4` = twice a week).
- Add more topics any time by editing `data/topics.json` — no code changes
  needed.

## Cost note
Each article uses a modest number of Sarvam tokens. Watch your credit
balance on the Sarvam dashboard; when it runs low, either top up or reduce
posting frequency in the workflow's cron schedule.
