#!/usr/bin/env python3
"""
Scrape the CEGH GreenHydrogen Index (Austria) into json/cegh_index.json.

CEGH publishes these as plain server-rendered HTML tables (ids ppa100,
ppa40, spot, GreenHydrogenForward) at the URL below — no API, no JS
rendering needed, just requests + BeautifulSoup.

HYCLICX (HyXchange) and HYDRIX (EEX) are NOT handled here — HYCLICX's
hourly data is only available on request (no public page to scrape), and
HYDRIX needs a webshop account/token to confirm free access. Those stay
stubs until one of those access questions is resolved.

CEGH publishes in EUR/MWh on a High Heating Value (HHV) basis. HHV of
hydrogen is 141.8 MJ/kg = 39.4 kWh/kg, so EUR/kg = EUR/MWh * 39.4 / 1000.
(Not the LHV figure, 33.3 kWh/kg — that conversion was used by mistake in
this project's first draft and has been corrected.)
"""
import json
import os
import re
import time
import requests
from bs4 import BeautifulSoup

URL = "https://www.cegh.at/en/greengas/cegh-greenhydrogen-index/"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "json", "cegh_index.json")

KWH_PER_KG_HHV = 39.4
HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) HydrogenPriceWatch/0.1"}


def eur_per_kg(eur_per_mwh):
    return round(eur_per_mwh * KWH_PER_KG_HHV / 1000, 2)


def parse_num(text):
    return float(text.strip().replace(",", ""))


def parse_single_row_table(soup, table_id, label):
    table = soup.find("table", id=table_id)
    if not table:
        return None
    row = table.find("tbody").find("tr") if table.find("tbody") else table.find_all("tr")[1]
    cells = row.find_all("td")
    delivery_period = cells[0].get_text(strip=True)
    value = parse_num(cells[1].get_text(strip=True))
    return {
        "label": label,
        "delivery_period": delivery_period,
        "eur_per_mwh": value,
        "eur_per_kg": eur_per_kg(value),
    }


def parse_forward_table(soup, table_id):
    table = soup.find("table", id=table_id)
    if not table:
        return []
    rows = table.find_all("tr")[1:]  # skip header row
    out = []
    for row in rows:
        cells = row.find_all("td")
        if len(cells) < 3:
            continue
        delivery_period = cells[0].get_text(strip=True)
        maturity = cells[1].get_text(strip=True)
        value = parse_num(cells[2].get_text(strip=True))
        out.append({
            "delivery_period": delivery_period,
            "maturity": maturity,
            "eur_per_mwh": value,
            "eur_per_kg": eur_per_kg(value),
        })
    return out


def parse_publication_date(soup):
    el = soup.find("h3", class_="h6")
    if not el:
        return None
    m = re.search(r"(\d{2})\.(\d{2})\.(\d{4})", el.get_text())
    if not m:
        return None
    day, month, year = m.groups()
    return f"{year}-{month}-{day}"


def main():
    resp = requests.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.text, "html.parser")

    ppa100 = parse_single_row_table(soup, "ppa100", "GreenHydrogen Index — PPA 100% (RED II / Delegated Act compliant)")
    ppa40 = parse_single_row_table(soup, "ppa40", "GreenHydrogen PPA 40 Index (not compliant)")
    spot = parse_single_row_table(soup, "spot", "GreenHydrogen Spot Index (not compliant)")
    forward = parse_forward_table(soup, "GreenHydrogenForward")
    pub_date = parse_publication_date(soup)

    if not (ppa100 or ppa40 or spot):
        out = {"status": "error", "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
               "note": "Could not find expected tables — CEGH may have changed their page markup."}
    else:
        out = {
            "status": "ok",
            "source": "CEGH GreenHydrogen Index",
            "source_url": URL,
            "publication_date": pub_date,
            "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "unit_basis": "EUR/MWh, High Heating Value (HHV)",
            "conversion": {
                "kwh_per_kg_hhv": KWH_PER_KG_HHV,
                "note": "eur_per_kg = eur_per_mwh * kwh_per_kg_hhv / 1000",
            },
            "ppa100": ppa100,
            "ppa40": ppa40,
            "spot": spot,
            "forward": forward,
        }

    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {OUT_PATH} (status={out['status']})")


if __name__ == "__main__":
    main()
