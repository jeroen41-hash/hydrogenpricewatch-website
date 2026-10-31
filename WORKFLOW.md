# HydrogenPriceWatch — workflow & status

Plain static HTML/CSS/JS site (no Jekyll/build step), same pattern as
dirtiestships/cleanestships: pages fetch JSON from `json/` at runtime.
Chose this over the hydrogenshipbuilding Jekyll stack to avoid a Ruby/bundler
dependency for what's currently a 4-page site.

## What's real right now

- **News** (`json/news.json`) — live. `scripts/news_scraper.py` pulls RSS
  from Hydrogen Fuel News, Fuel Cells Works, Hydrogen Europe, and Hydrogen
  Central (30 items, real headlines as of today). Hydrogen Insight's feed
  URL (`hydrogeninsight.com/rss`) currently fails to parse — needs a fixed
  feed URL or a `requests`-with-User-Agent fetch before handing to
  `feedparser` (likely bot-blocked).
- Site renders correctly: all 4 pages + CSS/JS/JSON assets return HTTP 200
  from a local static server; JSON files validate; Python scripts compile.
  Not yet checked in an actual browser.

## What's still a placeholder

- **Prices** (`json/price_snapshot.json`, `json/price_history.json`,
  `json/market_prices.json`) — hand-written illustrative numbers, clearly
  tagged `"status": "placeholder"` in the JSON and "sample data" on the
  page. `scripts/price_scraper.py` is a stub explaining why: none of
  HYCLICX / HYDRIX / CEGH can be pulled automatically yet (see
  `sources.html`).

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
7. **CEGH index scraper** — write the actual HTML scrape against the
   public page once someone's looked at its real markup.

## Running the news scraper

```
cd "/media/jeroen/work/16_Claude/hydrogenpricewatch"
./venv/bin/python3 scripts/news_scraper.py
```

Not yet on a cron — add a line on the Debian PC's ship-registry crontab
pattern once this repo is cloned there, same as the other site scrapers.
