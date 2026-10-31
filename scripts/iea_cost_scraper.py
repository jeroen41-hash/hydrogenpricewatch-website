#!/usr/bin/env python3
"""
Scrape ACER's republished IEA hydrogen production cost ranges into
json/iea_hydrogen_costs.json.

ACER's CHEST portal (aegis.acer.europa.eu) republishes IEA Global Hydrogen
Review figures as a plain server-rendered HTML table (id=datasetTable1535)
— the whole dataset is in the page source, no need to drive the CSV/Excel
export flow (which requires picking a "reason for export" in a dropdown).

This gives real EUR2024/kg cost RANGES by technology and year (2024 vs a
2030 projection) — not a live price, but a credible, citable benchmark to
replace guesswork for the grey/blue/green comparison.
"""
import json
import os
import time
import requests
from bs4 import BeautifulSoup

URL = "https://aegis.acer.europa.eu/chest/dataitems/972/view"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "json", "iea_hydrogen_costs.json")
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HydrogenPriceWatch/0.1"}

# Which IEA technology categories count as which pathway for this site.
PATHWAY_MAP = {
    "grey": ["Natural gas without CCUS", "Coal without CCUS"],
    "blue": ["Natural gas with CCUS", "Coal with CCUS"],
    "green": ["Solar PV", "Wind onshore", "Wind offshore"],
}
REPORT_FILTER = "IEA Global Hydrogen Review 2025"


def scrape_rows():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id="datasetTable1535")
    rows = []
    for tr in table.find("tbody").find_all("tr"):
        cells = [td.get_text(strip=True) for td in tr.find_all("td")]
        if len(cells) != 6:
            continue
        technology, report, year, agg, eur_kg, eur_mwh = cells
        rows.append({
            "technology": technology,
            "report": report,
            "year": int(year),
            "aggregation": agg,
            "eur_per_kg": float(eur_kg),
            "eur_per_mwh": float(eur_mwh),
        })
    return rows


def pathway_range(rows, technologies, year):
    mins, maxs = [], []
    for r in rows:
        if r["report"] != REPORT_FILTER or r["year"] != year or r["technology"] not in technologies:
            continue
        if r["aggregation"] == "Minimum":
            mins.append(r["eur_per_kg"])
        elif r["aggregation"] == "Maximum":
            maxs.append(r["eur_per_kg"])
    if not mins or not maxs:
        return None
    return {"min": round(min(mins), 2), "max": round(max(maxs), 2)}


def main():
    rows = scrape_rows()
    pathways = {}
    for pathway, technologies in PATHWAY_MAP.items():
        y2024 = pathway_range(rows, technologies, 2024)
        y2030 = pathway_range(rows, technologies, 2030)
        pathways[pathway] = {
            "technologies": technologies,
            "2024": y2024,
            "2030": y2030,
        }

    out = {
        "status": "ok" if rows else "error",
        "source": f"{REPORT_FILTER} (via ACER CHEST)",
        "source_url": URL,
        "unit": "EUR2024/kg",
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "note": "2030 figures are IEA projections (States Energy Policies scenario in the 2025 edition), not forecasts specific to this site.",
        "pathways": pathways,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_PATH} (status={out['status']}, {len(rows)} rows scraped)")


if __name__ == "__main__":
    main()
