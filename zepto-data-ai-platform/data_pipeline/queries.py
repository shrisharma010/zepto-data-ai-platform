import sqlite3
import pandas as pd

DB_PATH = "books.db"

QUERIES = {
    "1. High-rated books in stock (SELECT, WHERE)": """
        SELECT title, rating, price_inr, in_stock
        FROM books
        WHERE rating >= 4 AND in_stock = 1
        LIMIT 5;
    """,
    "2. Top 10 most expensive books (ORDER BY, LIMIT)": """
        SELECT title, price_inr, rating
        FROM books
        ORDER BY price_inr DESC
        LIMIT 10;
    """,
    "3. Distinct ratings present in database (DISTINCT)": """
        SELECT DISTINCT rating
        FROM books
        ORDER BY rating ASC;
    """,
    "4. Books with price_gbp between 20 and 40 (BETWEEN)": """
        SELECT title, price_gbp, price_inr
        FROM books
        WHERE price_gbp BETWEEN 20 AND 40
        LIMIT 5;
    """,
    "5. Books in Travel & Mystery with category name (IN, JOIN)": """
        SELECT b.title, c.category_name, b.price_inr, b.rating
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        WHERE c.category_name IN ('Travel', 'Mystery')
        LIMIT 10;
    """,
    "6. Top 3 highest-rated books per category (JOIN, Window Subquery)": """
        WITH RankedBooks AS (
            SELECT b.title, c.category_name, b.rating, b.price_inr,
                   ROW_NUMBER() OVER (PARTITION BY b.category_id ORDER BY b.rating DESC, b.price_inr DESC) AS rank
            FROM books b
            JOIN categories c ON b.category_id = c.category_id
        )
        SELECT category_name, rank, title, rating, price_inr
        FROM RankedBooks
        WHERE rank <= 3;
    """
}

def run_queries_and_log():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    markdown_lines = ["# Module 1: SQL Query Results\n"]

    print("--- Executing SQL Queries ---")
    for name, sql in QUERIES.items():
        print(f"\nRunning: {name}")
        cursor.execute(sql)
        cols = [d[0] for d in cursor.description]
        rows = cursor.fetchall()

        df_res = pd.DataFrame(rows, columns=cols)
        print(df_res.head())

        markdown_lines.append(f"## {name}\n")
        markdown_lines.append("```sql")
        markdown_lines.append(sql.strip())
        markdown_lines.append("```\n")
        markdown_lines.append("```text")
        markdown_lines.append(df_res.to_string(index=False))
        markdown_lines.append("```\n")

    with open("data_pipeline/sql_results.md", "w", encoding="utf-8") as f:
        f.write("\n".join(markdown_lines))

    print("\n[OK] Wrote all query outputs to data_pipeline/sql_results.md")

    # Step 1.6 Pandas Equivalence Check
    print("\n--- Running Pandas Equivalence Test ---")
    join_sql = """
        SELECT b.title, c.category_name, b.price_inr, b.rating
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        WHERE c.category_name IN ('Travel', 'Mystery')
        ORDER BY b.title ASC;
    """
    sql_df = pd.read_sql(join_sql, conn)

    # Pure pandas merge equivalent
    books_df = pd.read_sql("SELECT * FROM books", conn)
    cats_df = pd.read_sql("SELECT * FROM categories", conn)

    merged = books_df.merge(cats_df, on="category_id")
    filtered = merged[merged["category_name"].isin(["Travel", "Mystery"])]
    pandas_df = filtered[["title", "category_name", "price_inr", "rating"]].sort_values("title")

    pd.testing.assert_frame_equal(
        sql_df.reset_index(drop=True),
        pandas_df.reset_index(drop=True),
        check_dtype=False
    )
    print("SQL output head:")
    print(sql_df.head(3))
    print("Pandas merge output head:")
    print(pandas_df.head(3))
    print("[Assertion Passed] SQL and pandas results match perfectly!")

    # Additional pd.read_sql call
    avg_price_df = pd.read_sql("""
        SELECT c.category_name, ROUND(AVG(b.price_inr), 2) AS avg_price_inr
        FROM books b
        JOIN categories c ON b.category_id = c.category_id
        GROUP BY c.category_name;
    """, conn)
    print("\nAdditional Query via pd.read_sql (Average price per category):")
    print(avg_price_df)

    conn.close()

if __name__ == "__main__":
    run_queries_and_log()