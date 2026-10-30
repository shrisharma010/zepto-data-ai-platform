# Module 1: Data Pipeline

## Overview
This module scrapes product data across four categories from books.toscrape.com, handles messy records, converts currency, loads normalized data into an SQLite relational database, and executes analytical SQL queries with pandas equivalence verification.

## Scraped Categories
- Travel (`travel_2`)
- Mystery (`mystery_3`)
- Historical Fiction (`historical-fiction_4`)
- Classics (`classics_6`)

## Setup & Execution
From the repository root:
```powershell
pip install -r data_pipeline/requirements.txt
python data_pipeline/scrape_clean_load.py
python data_pipeline/queries.py