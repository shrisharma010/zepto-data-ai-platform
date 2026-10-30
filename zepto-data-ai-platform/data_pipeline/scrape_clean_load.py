import os
import re
import sqlite3
import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd

BASE = "https://books.toscrape.com/catalogue/category/books/"
CATEGORIES = {
    "Travel": "travel_2",
    "Mystery": "mystery_3",
    "Classics": "classics_6",
    "Historical Fiction": "historical-fiction_4",
}
RATING_MAP = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
GBP_TO_INR = 105.50

def scrape_category(name, slug):
    url = f"{BASE}{slug}/index.html"
    rows = []
    print(f"Scraping category: {name}...")
    while url:
        r = requests.get(url, timeout=15)
        r.raise_for_status()
        r.encoding = "utf-8"
        soup = BeautifulSoup(r.text, "html.parser")
        for pod in soup.select("article.product_pod"):
            rows.append({
                "title": pod.h3.a["title"],
                "price": pod.select_one("p.price_color").text.strip(),
                "star_rating": pod.select_one("p.star-rating")["class"][1],
                "availability": pod.select_one("p.availability").text.strip(),
                "category": name,
            })
        nxt = soup.select_one("li.next a")
        url = urljoin(url, nxt["href"]) if nxt else None
        time.sleep(0.5)
    return rows

def parse_price(s):
    m = re.search(r"[\d.]+", str(s))
    return float(m.group()) if m else None

def main():
    # 1. Scrape all categories
    all_rows = []
    for name, slug in CATEGORIES.items():
        all_rows.extend(scrape_category(name, slug))
    
    df = pd.DataFrame(all_rows)
    print(f"Total raw rows scraped: {len(df)}")
    assert len(df) >= 60, "Scraped less than 60 books!"
    assert df["category"].nunique() >= 3, "Scraped fewer than 3 categories!"

    # 2. Clean data
    df["price_gbp"] = df["price"].apply(parse_price)
    median_price = df["price_gbp"].median()
    df["price_gbp"] = df["price_gbp"].fillna(median_price)

    df["rating"] = df["star_rating"].map(RATING_MAP)
    df = df.dropna(subset=["rating"])  # Drop unmappable ratings safely
    df["rating"] = df["rating"].astype(int)

    df["in_stock"] = df["availability"].str.contains("in stock", case=False, na=False)
    df["in_stock"] = df["in_stock"].astype(bool)

    # 3. Currency Conversion
    df["price_inr"] = (df["price_gbp"] * GBP_TO_INR).round(2)

    # 4. Load into SQLite Database (Regenerate from scratch)
    db_path = "books.db"
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON;")

    cursor.execute("""
        CREATE TABLE categories (
            category_id INTEGER PRIMARY KEY,
            category_name TEXT UNIQUE NOT NULL
        );
    """)

    cursor.execute("""
        CREATE TABLE books (
            book_id INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            price_gbp REAL,
            price_inr REAL,
            rating INTEGER CHECK (rating BETWEEN 1 AND 5),
            in_stock INTEGER,
            category_id INTEGER NOT NULL REFERENCES categories(category_id)
        );
    """)

    # Insert categories
    unique_cats = df["category"].unique()
    cat_id_map = {}
    for cat in unique_cats:
        cursor.execute("INSERT INTO categories (category_name) VALUES (?)", (cat,))
        cat_id_map[cat] = cursor.lastrowid

    # Insert books
    for _, row in df.iterrows():
        cat_id = cat_id_map[row["category"]]
        cursor.execute("""
            INSERT INTO books (title, price_gbp, price_inr, rating, in_stock, category_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (row["title"], row["price_gbp"], row["price_inr"], row["rating"], int(row["in_stock"]), cat_id))

    conn.commit()
    conn.close()
    print("Module 1 pipeline completed successfully! Database 'books.db' generated.")

if __name__ == "__main__":
    main()