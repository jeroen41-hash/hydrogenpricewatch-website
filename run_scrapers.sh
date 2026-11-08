#!/bin/bash
set -e
cd ~/hydrogenpricewatch-website
git pull --ff-only origin main

VENV=~/ship-registry/venv/bin/python3
$VENV scripts/news_scraper.py
$VENV scripts/price_scraper.py
$VENV scripts/iea_cost_scraper.py
$VENV scripts/acer_lcoh_scraper.py
$VENV scripts/build_homepage_data.py

if ! git diff --quiet; then
  git add -A
  git commit -m "Automated data refresh $(date -u +%Y-%m-%dT%H:%M:%SZ)

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>"
  git push origin main
  echo "pushed update"
else
  echo "no changes"
fi
