#!/usr/bin/env python3
"""
STUB — price scraper for HydrogenPriceWatch.

None of the three real indices identified in sources.html can be pulled
automatically yet:
  - HyXchange HYCLICX: hourly data is available only on request (email the
    HyXchange team) — no public API to hit here.
  - EEX HYDRIX: webshop claims free real-time access, but needs an EEX
    webshop account/token to confirm and pull — unverified.
  - CEGH GreenHydrogen Index: public page shows current values but needs a
    scraper written against CEGH's actual HTML, not yet done.

Until one of these is wired up, json/price_snapshot.json and
json/price_history.json stay hand-edited placeholders (see their "status":
"placeholder" field). Next step: pick one source, confirm access, and
replace this stub with a real fetch + write, following the same shape as
news_scraper.py.
"""

if __name__ == "__main__":
    print(__doc__)
