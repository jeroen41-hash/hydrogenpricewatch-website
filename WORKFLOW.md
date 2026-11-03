# HydrogenPriceWatch — workflow & status

Plain static HTML/CSS/JS site (no Jekyll/build step), same pattern as
dirtiestships/cleanestships: pages fetch JSON from `json/` at runtime.
Chose this over the hydrogenshipbuilding Jekyll stack to avoid a Ruby/bundler
dependency for what's currently a 4-page site.

## What's real right now

- **News** (`json/news.json`) — live. `scripts/news_scraper.py` pulls RSS
  from Hydrogen Fuel News, Fuel Cells Works, Hydrogen Europe, Hydrogen
  Central, and pv magazine's hydrogen tag feed (30 items, real headlines,
  all 5 feeds parsing cleanly as of 2026-11-03). Hydrogen Insight was
  dropped: its feed now redirects through a login/paywall gate and its
  robots.txt explicitly disallows AI bots (`anthropic-ai`, `Claude-Web`,
  `ClaudeBot`) — a deliberate site-operator signal, not something to
  route around. gasworld.com has the same explicit disallow. h2-view.com's
  feed parses but is empty. canarymedia.com has no hydrogen-specific feed
  and its sitewide feed is too low-signal for hydrogen content.
- Site renders correctly: all 4 pages + CSS/JS/JSON assets return HTTP 200
  from a local static server; JSON files validate; Python scripts compile.
  Not yet checked in an actual browser.

- **CEGH GreenHydrogen Index** (`json/cegh_index.json`) — live. CEGH
  publishes PPA 100% (RED II compliant), PPA 40, spot, and an 8-point
  forward curve as plain server-rendered HTML tables, no API or headless
  browser needed. `scripts/price_scraper.py` scrapes it with
  requests + BeautifulSoup and converts EUR/MWh (HHV) to EUR/kg using
  39.4 kWh/kg HHV (not 33.3, which is the LHV figure — an earlier draft
  of this project used the wrong one). Shown on the home page as its own
  "Live index" box, and as the Austria row in the by-market table.

- **IEA production cost ranges** (`json/iea_hydrogen_costs.json`) — real, but not live. ACER's CHEST portal republishes the full IEA Global Hydrogen Review dataset as a plain server-rendered HTML table (`#datasetTable1535`), no login or CSV-export flow needed. `scripts/iea_cost_scraper.py` scrapes it and groups technologies into grey/blue/green EUR/kg ranges for 2024 vs. a 2030 projection. Shown on the home page as "Production cost ranges by pathway."
- **Other sources researched and ruled out**: China's SMM "Hydrogen Price Index" has real numbers but an explicit no-copying notice plus a partial paywall. Japan/Korea have no free hydrogen $/kg index (Argus/Platts price ammonia, not hydrogen, subscription-only). EU Hydrogen Bank and UK HAR auction clearing prices are real €/£-per-kg numbers but one-off events — good news-feed material, not a continuous price series; not built yet.

## Snapshot cards, forward-curve chart, and by-market table are now real

`scripts/build_homepage_data.py` derives `json/price_snapshot.json`,
`json/price_history.json`, and `json/market_prices.json` from the two real
scraped sources (`cegh_index.json`, `iea_hydrogen_costs.json`) — no more
hand-written placeholder numbers:

- **Green** snapshot card + the home page chart = CEGH's live PPA100 price
  and real forward curve (Austria only).
- **Grey/blue** snapshot cards = IEA's 2024 cost benchmark range (real
  published figures, but not a live price — only changes with a new
  Global Hydrogen Review edition).
- **By-market table** only lists Austria (the one market with a verified
  source); the fabricated China/US/India/Netherlands/Germany/Australia
  rows were removed rather than left as fake numbers. More rows get added
  as HYCLICX/HYDRIX access is secured.

Run this script after `price_scraper.py` and `iea_cost_scraper.py` (it
reads their output). None of HYCLICX / HYDRIX can be pulled automatically
yet (see `sources.html`).

## Manual steps before this can go live

1. **Domain** — hydrogenpricewatch.com not registered. Check availability
   and register (same registrar pattern as voyagedistance: Porkbun) — I
   did not do this myself, it costs money.
2. **GitHub repo** — create an empty repo (e.g.
   `jeroen41-hash/hydrogenpricewatch-website`) and I'll add the remote +
   push; `gh` isn't installed on this machine so this has to be done via
   the GitHub web UI or `git remote add` + token.
3. **GA4 property** — create one for this site, then replace
   `G-XXXXXXXXXX` across all 4 HTML files with the real ID.
4. **AdSense** — add once there's traffic; `privacy.html` already mentions
   it.
5. **HYCLICX hourly data** — email the HyXchange team to request access;
   no public API.
6. **EEX HYDRIX** — confirm the webshop's "free of charge" terms still
   hold and get an account/token.

## Running the scrapers

**Live on cron (2026-11-03)**: the Debian PC (`jeroen@192.168.2.62`) has its
own clone at `~/hydrogenpricewatch-website/`, using the shared
`~/ship-registry/venv/` (already has requests/feedparser/beautifulsoup4 —
no separate venv needed). `~/hydrogenpricewatch-website/run_scrapers.sh`
does `git pull` → runs all four scripts in order → `git add -A && commit
&& push` only if something actually changed. Cron entry:

```
10 7 * * * ~/hydrogenpricewatch-website/run_scrapers.sh >> ~/hydrogenpricewatch-website/cron.log 2>&1
```

One daily run covers all three sources: CEGH updates its page daily, news
is obviously daily, and the IEA/ACER benchmark only changes per Global
Hydrogen Review edition (a no-op most days, which is fine).

Manual run (either checkout, e.g. for testing):

```
cd "/media/jeroen/work/16_Claude/hydrogenpricewatch"   # or ~/hydrogenpricewatch-website on the Debian PC
./venv/bin/python3 scripts/news_scraper.py             # (or ~/ship-registry/venv/bin/python3 on the Debian PC)
./venv/bin/python3 scripts/price_scraper.py
./venv/bin/python3 scripts/iea_cost_scraper.py
./venv/bin/python3 scripts/build_homepage_data.py
```

`build_homepage_data.py` must run last — it reads the output of the two
scrapers above and regenerates the snapshot/chart/market-table JSON.
