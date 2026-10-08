"""Create the self-contained sample shop database."""

from pathlib import Path
import sqlite3

DB_PATH = Path(__file__).parent / "data" / "sample_shop.db"


def create_database(path: Path = DB_PATH) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(path) as con:
        con.executescript("""
            PRAGMA foreign_keys = ON;
            DROP TABLE IF EXISTS order_items;
            DROP TABLE IF EXISTS orders;
            DROP TABLE IF EXISTS products;
            CREATE TABLE products (
                product_id INTEGER PRIMARY KEY,
                product_name TEXT NOT NULL,
                category TEXT NOT NULL,
                unit_price REAL NOT NULL
            );
            CREATE TABLE orders (
                order_id INTEGER PRIMARY KEY,
                order_date TEXT NOT NULL,
                customer_name TEXT NOT NULL,
                region TEXT NOT NULL
            );
            CREATE TABLE order_items (
                order_item_id INTEGER PRIMARY KEY,
                order_id INTEGER NOT NULL REFERENCES orders(order_id),
                product_id INTEGER NOT NULL REFERENCES products(product_id),
                quantity INTEGER NOT NULL,
                unit_price REAL NOT NULL
            );
        """)
        con.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", [
            (1, "Wireless Headphones", "Electronics", 79.99),
            (2, "Insulated Bottle", "Home", 24.50),
            (3, "Desk Lamp", "Home", 42.00),
            (4, "Mechanical Keyboard", "Electronics", 95.00),
            (5, "Canvas Backpack", "Accessories", 54.00),
            (6, "USB-C Hub", "Electronics", 38.00),
        ])
        con.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", [
            (101, "2026-09-02", "Maya Hassan", "Cairo"),
            (102, "2026-09-04", "Omar Adel", "Alexandria"),
            (103, "2026-09-08", "Nour Samy", "Cairo"),
            (104, "2026-09-12", "Youssef Ali", "Giza"),
            (105, "2026-09-18", "Laila Mostafa", "Cairo"),
            (106, "2026-09-23", "Karim Nabil", "Alexandria"),
            (107, "2026-09-25", "Salma Tarek", "Giza"),
        ])
        con.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?, ?)", [
            (1, 101, 1, 2, 79.99), (2, 101, 2, 1, 24.50),
            (3, 102, 4, 1, 95.00), (4, 102, 6, 2, 38.00),
            (5, 103, 1, 1, 79.99), (6, 103, 3, 2, 42.00),
            (7, 104, 5, 1, 54.00), (8, 104, 2, 3, 24.50),
            (9, 105, 4, 2, 95.00), (10, 105, 6, 1, 38.00),
            (11, 106, 1, 1, 79.99), (12, 106, 5, 2, 54.00),
            (13, 107, 3, 1, 42.00), (14, 107, 2, 2, 24.50),
        ])
    return path


if __name__ == "__main__":
    print(f"Sample database ready: {create_database()}")
