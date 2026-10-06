# DFW Nurse Residency Watch

Checks the websites of 59 Dallas–Fort Worth hospitals (12 health systems) for
new-graduate **nurse residency** openings, and tells you when a cohort that
starts in **August 2027 or later** is posted.

- **Runs on its own.** A GitHub Action checks every 3 hours. Hospitals near
  your home are checked on every run, ones within 30 miles twice a day, and
  the rest of DFW once a day.
- **Alerts you.** When a matching cohort shows up, it opens a GitHub issue,
  and GitHub emails you about it. 🎯 = start date is in your window,
  ❓ = new residency posting where the start date isn't clear.
- **Keeps a database.** Every posting, the date it was first and last seen,
  and every check are stored in SQLite (`data/residencies.sql`).
- **[REPORT.md](REPORT.md)** is the dashboard: matching cohorts sorted by
  distance, recent activity, earlier cohorts (useful for seeing when each
  hospital usually opens applications), every hospital by priority, and
  whether each website check is working.

## Setup (one time)

1. **Set your home location.** On GitHub, go to *Settings → Secrets and
   variables → Actions → Variables*, then add `HOME_ZIP` (for example `75024`).
   You can use `HOME_LAT` and `HOME_LON` instead if you want exact
   coordinates. Until this is set, every hospital is checked once a day and
   none is ranked by distance.
2. **Make the repo private.** The report lists each hospital's distance from
   your home, which roughly gives away where you live.
3. **Turn on notifications.** Click *Watch → All Activity* on the repo so
   that new issues reach your email or the GitHub app.
4. **Run it once now.** Go to *Actions → Check residencies → Run workflow*
   and tick **force**. After the first run, look at the *Source health* table
   in REPORT.md: any ❌ row is a URL that needs to be fixed in
   `hospitals.yaml`.

## Changing things

| To… | Edit |
|---|---|
| Change the target cohort window | `target_from` / `target_until` in `config.yaml` |
| Check near-home hospitals more or less often, or change what counts as near | `priority_tiers` in `config.yaml` |
| Always treat a hospital as top priority | add its id to `favorites` in `config.yaml` |
| Add a hospital or fix a URL | `hospitals.yaml` |
| Only get emails for 🎯 alerts, not ❓ | `alerts.issue_levels: [high]` |

## How it decides what's relevant

- **Job boards** (`kind: jobs`): finds job titles that look like an RN residency
  ("Graduate Nurse Residency", "New Grad RN Residency", "Nurse Resident",
  StaRN, PB-RNR…). It skips pharmacy and physician residencies,
  externships, and similar roles. It then reads the cohort from the title.
- **Program pages** (`kind: page`): finds sentences that mention a cohort or
  start date, such as "October 2027 cohort", "Fall 2027", or "February 2028".
  It also picks up wording like "applications now open" or "closed", and
  logs it when the page changes.
- Dates are sorted into: **target** (starts in your window), **maybe** (for
  example "Summer 2027", which could mean June or August), **early**, or
  **unknown**. The first check of each site is a baseline: it only alerts for
  target or maybe dates, so you don't get flooded on day one.
- A posting counts as removed after it's missing from two checks in a row.

## Running it locally

```bash
pip install -r requirements.txt
python -m playwright install chromium     # optional: for JavaScript-heavy job sites
HOME_ZIP=75024 python -m residency_watch hospitals   # see the priority order
HOME_ZIP=75024 python -m residency_watch run --force # check everything now
python -m residency_watch run --only thr bsw         # just some systems/sources
sqlite3 data/residencies.db "select title, cohort, relevance from findings where active"
python -m pytest
```
