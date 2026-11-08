#!/usr/bin/env python3
"""Scrape two more ACER CHEST dataitems for real hydrogen cost data:

- dataitem 970: LCOH by electricity-price threshold for Germany and Spain
  -> json/acer_country_lcoh.json
- dataitem 973: average RFNBO production cost + DK/NL/DE network transport
  tariffs + a transport cost range -> json/acer_delivered_cost.json

Same pattern as iea_cost_scraper.py: the "export" flow in the UI looks
gated, but the full dataset is already server-rendered in a plain HTML
table, so a login/export flow is never needed.
"""
import json
import os
import time
import requests
from bs4 import BeautifulSoup

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JSON_DIR = os.path.join(ROOT, "json")

HEADERS = {"User-Agent": "HydrogenPriceWatchBot/1.0 (+https://hydrogenpricewatch.com)"}


def fetch_table(url, table_id):
    resp = requests.get(url, headers=HEADERS, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")
    table = soup.find("table", id=table_id)
    if not table:
        raise ValueError(f"table {table_id} not found at {url}")
    rows = []
    for tr in table.find_all("tr"):
        cells = [c.get_text(strip=True) for c in tr.find_all(["th", "td"])]
        if cells:
            rows.append(cells)
    return rows


def parse_country_lcoh():
    url = "https://aegis.acer.europa.eu/chest/dataitems/970/view"
    rows = fetch_table(url, "datasetTable1534")
    header, data_rows = rows[0], rows[1:]
    countries = {}
    for country, threshold, eur_kg, eur_mwh in data_rows:
        countries.setdefault(country, []).append({
            "threshold_eur_mwh": float(threshold.split()[0]),
            "eur_per_kg": float(eur_kg),
            "eur_per_mwh": float(eur_mwh),
        })
    for vals in countries.values():
        vals.sort(key=lambda r: r["threshold_eur_mwh"], reverse=True)
    out = {
        "status": "ok",
        "source": "ACER CHEST — example LCOH by electricity-price threshold (DE, ES)",
        "source_url": url,
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "unit": "EUR/kg (and EUR/MWh)",
        "note": "Electrolyser LCOH at different electricity-price thresholds — a lower threshold means the electrolyser only runs on cheaper hours, so fewer running hours can raise the per-kg cost despite cheaper power. Not a live price.",
        "countries": countries,
    }
    with open(os.path.join(JSON_DIR, "acer_country_lcoh.json"), "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote acer_country_lcoh.json ({len(data_rows)} rows, {len(countries)} countries)")


def parse_delivered_cost():
    url = "https://aegis.acer.europa.eu/chest/dataitems/973/view"
    rows = fetch_table(url, "datasetTable1536")
    data_rows = rows[1:]
    values = {r[0]: {"eur_per_kg": float(r[1]), "eur_per_mwh": float(r[2])} for r in data_rows}
    out = {
        "status": "ok",
        "source": "ACER CHEST — RFNBO production cost vs. DK/DE/NL transport tariffs",
        "source_url": url,
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "unit": "EUR/kg (and EUR/MWh)",
        "note": "Average renewable (RFNBO) hydrogen production cost, plus what getting it to the end user adds on top via network tariffs in three countries. Not a live price.",
        "production_cost": values.get("Average production cost of RFNBO hydrogen"),
        "network_user_cost_by_country": {
            "Denmark": values.get("Network user costs in Denmark based on tariffs"),
            "Netherlands": values.get("Network user costs in Netherlands based on tariffs"),
            "Germany": values.get("Network user costs in Germany based on tariffs"),
        },
        "transport_cost_range": {
            "min": values.get("Transportation cost range (min)"),
            "max": values.get("Transportation cost range (max)"),
        },
    }
    with open(os.path.join(JSON_DIR, "acer_delivered_cost.json"), "w") as f:
        json.dump(out, f, indent=2)
    print("Wrote acer_delivered_cost.json")


def main():
    parse_country_lcoh()
    parse_delivered_cost()


if __name__ == "__main__":
    main()
