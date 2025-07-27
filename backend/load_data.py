import os
import pandas as pd
from sqlalchemy import create_engine
from datetime import datetime

# 1) Where to find your CSVs
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# 2) Path for your SQLite database (it will be created next to this script)
DB_PATH = os.path.join(os.path.dirname(__file__), "ecommerce.db")
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)

# 3) Helper to parse dates in any column containing these tokens
def parse_datetimes(df):
    for col in df.columns:
        if any(tok in col for tok in ("created", "shipped", "delivered", "returned", "at")):
            df[col] = pd.to_datetime(df[col], errors="coerce")
    return df

# 4) Map of table names → CSV filenames
TABLES = {
    "distribution_centers": "distribution_centers.csv",
    "inventory_items":      "inventory_items.csv",
    "order_items":          "order_items.csv",
    "orders":               "orders.csv",
    "products":             "products.csv",
    "users":                "users.csv",
}

if __name__ == "__main__":
    # Drop & re-create each table from its CSV
    for table, fname in TABLES.items():
        path = os.path.join(DATA_DIR, fname)
        print(f"Loading {path} into table `{table}`…")
        df = pd.read_csv(path)
        df = parse_datetimes(df)
        df.to_sql(table, engine, if_exists="replace", index=False)
        print(f"  → {len(df)} rows written to `{table}`")

    print("All CSVs loaded into SQLite:", DB_PATH)
