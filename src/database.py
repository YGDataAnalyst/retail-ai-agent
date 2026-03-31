# Script para crear tablas y cargar datos en una base de datos SQLite para el caso de una empresa de retail.

import sqlite3
import pandas as pd
from sqlalchemy import create_engine
import os


def setup_database():
    # Create the data folder if it doesn't exist
    if not os.path.exists("data"):
        os.makedirs("data")

    # Unique name for your professional database
    engine = create_engine("sqlite:///data/retail_pro.db")

    # 1. Dimension Products
    products = pd.DataFrame(
        {
            "product_id": [1, 2, 3, 4, 5, 6, 7],
            "product_name": [
                "Laptop Pro",
                "4K Monitor",
                "Mechanical Keyboard",
                "Ergonomic Mouse",
                "Gaming Chair",
                "USB-C Hub",
                "Wireless Headphones",
            ],
            "category": [
                "Hardware",
                "Hardware",
                "Peripherals",
                "Peripherals",
                "Furniture",
                "Accessories",
                "Accessories",
            ],
            "cost": [800, 200, 50, 20, 150, 30, 100],
            "sale_price": [1200, 350, 100, 45, 300, 60, 150],
            "current_stock": [5, 2, 50, 1, 10, 25, 15],
        }
    )

    # 2. Dimension Stores
    stores = pd.DataFrame(
        {
            "store_id": [1, 2, 3, 4, 5],
            "city": ["Madrid", "Barcelona", "Manchester", "Liverpool", "Birmingham "],
            "manager": [
                "Ana Silva",
                "Carlos Ruiz",
                "John Smith",
                "Emma Brown",
                "Michael Johnson",
            ],
        }
    )

    # 3. Fact Table Sales
    sales = pd.DataFrame(
        {
            "sale_id": range(101, 122),  # Generates IDs from 101 to 121
            "date": [
                "2024-02-10",
                "2024-02-15",
                "2024-02-20",
                "2024-02-25",  # February
                "2024-03-01",
                "2024-03-02",
                "2024-03-05",
                "2024-03-10",
                "2024-03-15",
                "2024-03-20",
                "2024-03-25",
                "2024-03-28",  # March
                "2024-04-01",
                "2024-04-05",
                "2024-04-10",
                "2024-04-15",
                "2024-04-20",
                "2024-04-25",
                "2024-04-30",
                "2024-05-05",
                "2024-05-10",
            ],
            "product_id": [
                1,
                2,
                3,
                4,
                1,
                2,
                1,
                3,
                4,
                1,
                2,
                3,
                4,
                5,
                6,
                7,
                1,
                2,
                3,
                4,
                5,
            ],  # Mixed products
            "store_id": [
                1,
                2,
                1,
                2,
                1,
                1,
                2,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
                2,
                1,
            ],  # Mixed stores
            "quantity": [
                1,
                2,
                5,
                10,
                1,
                1,
                2,
                3,
                5,
                1,
                1,
                4,
                2,
                3,
                1,
                5,
                2,
                3,
                1,
                4,
                2,
            ],  # Different volumes
        }
    )

    # Save everything in SQLite
    products.to_sql("dim_products", engine, index=False, if_exists="replace")
    stores.to_sql("dim_stores", engine, index=False, if_exists="replace")
    sales.to_sql("fact_sales", engine, index=False, if_exists="replace")

    return engine


if __name__ == "__main__":
    setup_database()
    print("✅ Database 'retail_pro.db' created successfully!")
