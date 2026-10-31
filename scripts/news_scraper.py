#!/usr/bin/env python3
"""Pull hydrogen-industry RSS feeds into json/news.json for the HydrogenPriceWatch site."""
import json
import os
import time
import feedparser

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_PATH = os.path.join(ROOT, "json", "news.json")

FEEDS = {
    "Hydrogen Insight": ("https://www.hydrogeninsight.com/rss", "Market"),
    "Hydrogen Fuel News": ("https://www.hydrogenfuelnews.com/feed", "Market"),
    "Fuel Cells Works": ("https://fuelcellsworks.com/feed/", "Infrastructure"),
    "Hydrogen Europe": ("https://hydrogeneurope.eu/feed/", "Policy"),
    "Hydrogen Central": ("https://hydrogen-central.com/feed/", "Market"),
}

MAX_ITEMS = 30
PER_FEED = 10


def fetch_feed(name, url, category):
    items = []
    try:
        parsed = feedparser.parse(url)
    except Exception as exc:
        print(f"  [skip] {name}: {exc}")
        return items
    if getattr(parsed, "bozo", False) and not parsed.entries:
        print(f"  [skip] {name}: feed did not parse ({parsed.bozo_exception})")
        return items
    for entry in parsed.entries[:PER_FEED]:
        title = entry.get("title", "").strip()
        link = entry.get("link", "").strip()
        if not title or not link:
            continue
        published = entry.get("published_parsed") or entry.get("updated_parsed")
        date_str = time.strftime("%Y-%m-%d", published) if published else ""
        sort_key = time.mktime(published) if published else 0
        items.append({
            "title": title,
            "url": link,
            "source": name,
            "category": category,
            "date": date_str,
            "_sort": sort_key,
        })
    return items


def main():
    all_items = []
    for name, (url, category) in FEEDS.items():
        print(f"Fetching {name} ...")
        fetched = fetch_feed(name, url, category)
        print(f"  got {len(fetched)} items")
        all_items.extend(fetched)

    all_items.sort(key=lambda it: it["_sort"], reverse=True)
    for it in all_items:
        del it["_sort"]
    all_items = all_items[:MAX_ITEMS]

    out = {
        "status": "ok" if all_items else "no_items",
        "updated": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "items": all_items,
    }
    with open(OUT_PATH, "w") as f:
        json.dump(out, f, indent=2)
    print(f"Wrote {len(all_items)} items to {OUT_PATH}")


if __name__ == "__main__":
    main()
