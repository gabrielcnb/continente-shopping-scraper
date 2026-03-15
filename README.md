# Continente Shopping Scraper

PyQt6 desktop app that searches and compares product prices on [Continente.pt](https://www.continente.pt) (Portuguese supermarket). Uses undetected-chromedriver to bypass bot detection.

## Features

- Search products by name with fuzzy matching
- Price comparison across multiple results
- Modern PyQt6 GUI
- Undetected Selenium (avoids bot detection)

## Stack

- Python 3.10+
- PyQt6 (GUI)
- Selenium + undetected-chromedriver
- fuzzywuzzy (fuzzy product name matching)

## Setup

```bash
pip install PyQt6 selenium undetected-chromedriver fuzzywuzzy python-Levenshtein
python beta.py
```

Requires Chrome installed.
