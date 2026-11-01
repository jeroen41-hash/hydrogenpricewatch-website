#!/usr/bin/env python3
"""Derive price_snapshot.json, price_history.json, and market_prices.json
from the real scraped sources (cegh_index.json, iea_hydrogen_costs.json).
Run after price_scraper.py and iea_cost_scraper.py.
"""
import json
from datetime import datetime, timezone
from pathlib import Path

JSON_DIR = Path(__file__).resolve().parent.parent / "json"


def load(name):
    with open(JSON_DIR / name) as f:
        return json.load(f)


def write(name, data):
    with open(JSON_DIR / name, "w") as f:
        json.dump(data, f, indent=2)
        f.write("\n")


def build_snapshot(cegh, iea):
    grey = iea["pathways"]["grey"]["2024"]
    blue = iea["pathways"]["blue"]["2024"]
    return {
        "status": "ok",
        "updated": datetime.now(timezone.utc).isoformat(),
        "note": "Green is a live market index (CEGH). Grey and blue are IEA's latest published cost benchmark — a real figure, but not a live price.",
        "grey": {
            "label": "Grey · unabated SMR/coal",
            "kind": "benchmark",
            "min": grey["min"],
            "max": grey["max"],
            "unit": "€/kg",
            "year": 2024,
            "source": "IEA Global Hydrogen Review 2025",
        },
        "blue": {
            "label": "Blue · SMR/coal + CCUS",
            "kind": "benchmark",
            "min": blue["min"],
            "max": blue["max"],
            "unit": "€/kg",
            "year": 2024,
            "source": "IEA Global Hydrogen Review 2025",
        },
        "green": {
            "label": "Green · electrolysis (Austria)",
            "kind": "live",
            "price": cegh["ppa100"]["eur_per_kg"],
            "unit": "€/kg",
            "source": "CEGH GreenHydrogen Index — PPA 100%",
            "as_of": cegh["publication_date"],
        },
    }


def build_chart(cegh):
    points = [{"label": "Spot (" + cegh["spot"]["delivery_period"] + ")", "value": cegh["spot"]["eur_per_kg"]}]
    for f in cegh["forward"]:
        points.append({"label": f["delivery_period"], "value": f["eur_per_kg"]})
    return {
        "status": "ok",
        "source": "CEGH GreenHydrogen Index — forward curve",
        "source_url": cegh["source_url"],
        "updated": cegh["updated"],
        "unit": "€/kg",
        "note": "Real forward curve for Austrian green hydrogen (RED II non-compliant spot/forward series). Not a prediction for other markets.",
        "points": points,
    }


def build_market(cegh):
    return {
        "status": "ok",
        "note": "Only markets with a verified public or semi-public source are listed. More will be added as additional feeds (HyXchange HYCLICX, EEX HYDRIX) are secured — see sources.html.",
        "rows": [
            {
                "market": "Austria",
                "pathway": "green",
                "source": "CEGH GreenHydrogen Index (live)",
                "price": "€" + str(cegh["ppa100"]["eur_per_kg"]) + "/kg",
            }
        ],
    }


def main():
    cegh = load("cegh_index.json")
    iea = load("iea_hydrogen_costs.json")
    write("price_snapshot.json", build_snapshot(cegh, iea))
    write("price_history.json", build_chart(cegh))
    write("market_prices.json", build_market(cegh))
    print("ok: wrote price_snapshot.json, price_history.json, market_prices.json")


if __name__ == "__main__":
    main()
