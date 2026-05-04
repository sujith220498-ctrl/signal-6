# Signal 6 — LinkedIn Profile Monitor

Monitor a list of LinkedIn profiles for new posts and comments. Filter for relevance to your ICP. Never see the same item twice.

Built as a [Claude Code](https://claude.ai/code) slash command. Runs in your terminal.

---

## What It Does

1. Fetches recent posts and comments from profiles you specify
2. Filters to comments from the last 14 days (configurable)
3. Deduplicates so you never see the same item twice across runs
4. Applies your relevance criteria — defined by you, not hardcoded
5. Prints a clean signal report to terminal

---

## Prerequisites

- [Claude Code](https://claude.ai/code) installed
- [Apify](https://apify.com) account — Starter plan ($29/month) works for weekly runs
- Apify CLI installed: `npm install -g apify-cli`
- Logged into Apify: `apify login`
- Python 3

---

## Setup

1. Clone this repo
2. Open Claude Code from inside the cloned folder
3. Edit `profiles.json` — add the LinkedIn URLs you want to monitor
4. Edit `relevance-prompt.md` — describe your ICP and what counts as a signal
5. Run `/signal-6`

---

## How to Run

Type `/signal-6` in Claude Code.

That's it.

---

## Configuration

### `profiles.json`
Add any LinkedIn profile URLs. As many as you need.

```json
[
  "https://www.linkedin.com/in/their-profile/",
  "https://www.linkedin.com/in/another-profile/"
]
```

### `relevance-prompt.md`
Describe your ICP, your signal keywords, what counts, and what doesn't. The filter reads only this file — nothing is hardcoded into the skill.

---

## Cost

Signal 6 uses two Apify actors to scrape LinkedIn. You need your own Apify account.

| Actor | Cost |
|---|---|
| Posts (`harvestapi/linkedin-profile-posts`) | Low — a few seconds per profile |
| Comments (`unseenuser/LinkedIn-user-comments-reactions`) | Higher — uses residential proxies |

**Recommended cadence: weekly.** The $29/month Starter plan supports ~4–6 runs/month comfortably.

The comments actor scrapes a profile's full comment history but Signal 6 filters to the last 14 days before surfacing anything. Adjust `RECENCY_DAYS` in `run.py` to match your run cadence.

---

## Files

| File | Edit? | Purpose |
|---|---|---|
| `profiles.json` | Yes | LinkedIn URLs to monitor |
| `relevance-prompt.md` | Yes | Your ICP and signal criteria |
| `run.py` | No | Fetch, filter by recency, deduplicate |
| `CLAUDE.md` | No | Slash command definition |
| `seen.json` | No — auto-created | Dedup log, updated each run |
| `new_items.json` | No — auto-created | Temp file from last run |

---

## Tuning

- **Change recency window** → edit `RECENCY_DAYS` in `run.py` (default: 14 days)
- **Add/remove profiles** → edit `profiles.json`
- **Change signal criteria** → edit `relevance-prompt.md`
- **See everything again** → delete `seen.json`

---

## Troubleshooting

| Problem | Fix |
|---|---|
| Posts actor fails | Check Apify dashboard — `harvestapi/linkedin-profile-posts` |
| Comments actor fails | Check Apify dashboard — `unseenuser/LinkedIn-user-comments-reactions` |
| Profile returns zero results | LinkedIn vanity URL may have changed — update `profiles.json` |
| Apify credits running low | Reduce run frequency or upgrade Apify plan |
