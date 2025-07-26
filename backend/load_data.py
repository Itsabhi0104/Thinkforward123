import pandas as pd
from models import db, DistributionCenter, InventoryItem, OrderItem, Order, Product, User
from app import create_app
from datetime import datetime

def parse_datetime(val):
    return pd.to_datetime(val) if not pd.isna(val) else None

def load_csv_to_db(session, model, csv_path, column_map=None):
    df = pd.read_csv(csv_path)
    if column_map:
        df = df.rename(columns=column_map)
    records = df.to_dict(orient='records')
    for rec in records:
        # parse any datetime-like fields
        for k, v in rec.items():
            if any(tok in k for tok in ('at', 'created', 'shipped', 'delivered', 'returned')):
                rec[k] = parse_datetime(v)
        session.add(model(**rec))
    session.commit()

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        session = db.session
        base = './data'
        load_csv_to_db(session, DistributionCenter, f'{base}/distribution_centers.csv')
        load_csv_to_db(session, Product,             f'{base}/products.csv')
        load_csv_to_db(session, InventoryItem,       f'{base}/inventory_items.csv')
        load_csv_to_db(session, Order,               f'{base}/orders.csv')
        load_csv_to_db(session, OrderItem,           f'{base}/order_items.csv')
        load_csv_to_db(session, User,                f'{base}/users.csv')
        print("Data loaded successfully.")
