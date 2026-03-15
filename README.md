# continente-shopping-scraper

Desktop app that automates grocery shopping on continente.pt — searches a list of items, selects the best match using fuzzy string matching, and processes each one sequentially.

## Features

- Accepts a list of grocery items and searches each one on continente.pt
- Fuzzy string matching (fuzzywuzzy) to select the best product result per search term
- Undetected ChromeDriver to bypass bot detection
- PyQt6 GUI with real-time progress bar, status label, and scrollable log output
- Browser automation runs in a background QThread, keeping the UI responsive
- Stop button to interrupt the session at any point
- Automatic cookie consent handling on startup

## Stack

| Component | Choice |
|-----------|--------|
| Language | Python 3 |
| GUI | PyQt6 |
| Browser automation | Selenium + undetected-chromedriver |
| String matching | fuzzywuzzy |
| ChromeDriver management | webdriver-manager |

## Setup / Installation

```bash
pip install PyQt6 selenium undetected-chromedriver webdriver-manager fuzzywuzzy python-Levenshtein
```

Google Chrome must be installed. The script targets Chrome version 132. If your installed version differs, update `version_main` in `beta.py`:

```python
driver = uc.Chrome(options=chrome_options, version_main=132)
```

## Usage

```bash
python beta.py
```

The GUI window opens. Enter your shopping list (one item per line) and click Start. The browser opens continente.pt, accepts cookies automatically, and processes each item. Results and errors are logged in real time in the GUI log panel.

## File Structure

```
compras continente/
└── beta.py    # Main application — GUI + background scraper worker
```
