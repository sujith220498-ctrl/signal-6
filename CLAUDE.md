# Signal 6 — LinkedIn Profile Monitor

## What This Skill Does

Monitors a fixed list of LinkedIn profiles for new posts and comments. Filters for relevance based on your ICP criteria. Deduplicates across runs so you never see the same item twice. Prints results to terminal.

---

## Setup (one time)

1. **Add your profiles** — edit `profiles.json` with the LinkedIn URLs you want to monitor
2. **Set your relevance criteria** — edit `relevance-prompt.md` to describe your ICP and what counts as a signal
3. **Log into Apify** — run `apify login` in terminal (uses your own Apify account)

That's it. Nothing else to configure.

---

## How to Run

Type `/signal-6` in Claude Code.

---

## Slash Command Instructions

When the user runs `/signal-6`, execute the following steps in order:

### Step 1 — Fetch and deduplicate

Run:
```bash
python3 run.py
```

This fetches posts and comments from all profiles in `profiles.json`, deduplicates against `seen.json`, and writes new items to `new_items.json`. Wait for it to complete before continuing.

### Step 2 — Read new items

Read `new_items.json` in the current directory.

If the file is empty or total items is 0, print:
```
No new signals. All items already seen.
```
And stop.

### Step 3 — Read relevance criteria

Read `relevance-prompt.md` in the current directory.

Use the criteria in that file — and only that file — to decide what is relevant. Do not use any other criteria.

### Step 4 — Apply relevance filter

For each item in `new_items.json`, evaluate the text against the criteria from `relevance-prompt.md`.

- If relevant: write one specific sentence summarising what the person expressed. Use their words where possible. Be specific, not generic.
- If not relevant: skip it entirely. Do not mention it in the output.

### Step 5 — Print formatted output

Print only the relevant items:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
SIGNAL MONITOR — [date], [time]
[X] relevant signals from [Y] new items checked.
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📌 POST — [Name]  ([time ago])
"[Full post text, up to 400 characters]"
[One sentence summary]
→ [url]

💬 COMMENT — [Name]  ([time ago])
"[Full comment text]"
[One sentence summary]
→ [url]
  (opens post — scroll to find their comment)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
[Y] items checked. [Y - X] skipped (not relevant).
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

If zero relevant items: `No relevant signals. [Y] items checked, all skipped.`

### Step 6 — Print weekly log

After the signal output, always print this block:

```
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
WEEKLY LOG — fill this in and send to Sujith
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Date: [date]
Profiles monitored: [number of profiles in profiles.json]
Items checked: [Y]
Signals found: [X]

Did you act on any signal this week? (comment, DM, saved for later)
→

What was useful? What was noise?
→

Anything you want to change? (profiles to add/remove, criteria to tune)
→
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

Pre-fill Date, Profiles monitored, Items checked, and Signals found. Leave the three arrow fields blank for the founder to fill in before sending.

---

## Files

| File | Who edits it | Purpose |
|---|---|---|
| `profiles.json` | You | LinkedIn URLs to monitor |
| `relevance-prompt.md` | You | Your ICP and signal criteria |
| `CLAUDE.md` | Nobody | Slash command instructions |
| `run.py` | Nobody | Fetch + dedup logic |
| `seen.json` | Auto | Dedup log — updated each run |
| `new_items.json` | Auto | Temp file — new items from last run |

---

## Maintenance

- **Add/remove profiles** → edit `profiles.json`
- **Tune what counts as a signal** → edit `relevance-prompt.md`
- **Reset dedup (see everything again)** → delete `seen.json`
- **Posts actor fails** → check Apify dashboard (`harvestapi/linkedin-profile-posts`)
- **Comments actor fails** → check Apify dashboard (`unseenuser/LinkedIn-user-comments-reactions`)
- **Profile returns zero results** → vanity URL may have changed, update `profiles.json`
