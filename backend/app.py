from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os

app = Flask(__name__)
CORS(app)

# ✅ Load CSVs
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

products_df = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
order_items_df = pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"))
inventory_df = pd.read_csv(os.path.join(DATA_DIR, "inventory_items.csv"))

# ✅ Map column names to consistent variables
# products.csv -> id, name
products_df = products_df.rename(columns={"id": "product_id", "name": "product_name"})

# order_items.csv -> product_id, sale_price
# inventory_items.csv -> product_id, product_name, quantity (not directly present, will count unsold items if needed)

sessions = {}
session_counter = 1


@app.route("/sessions", methods=["POST"])
def create_session():
    global session_counter
    data = request.json
    user_id = data.get("user_id", None)

    session_id = session_counter
    sessions[session_id] = {"user_id": user_id, "messages": []}
    session_counter += 1

    return jsonify({"session_id": session_id}), 201


@app.route("/chat", methods=["POST"])
def chat():
    data = request.json
    session_id = data.get("session_id")
    user_message = data.get("message", "").lower()

    if session_id not in sessions:
        return jsonify({"response": "Invalid session ID"}), 400

    response_text = "Sorry, I don't understand your question."

    # ✅ 1. Top 5 most sold products
    if "top" in user_message and "sold" in user_message:
        top_products = (
            order_items_df.groupby("product_id")["id"]  # "id" in order_items is unique per item sold
            .count()
            .sort_values(ascending=False)
            .head(5)
        )

        result = []
        for pid in top_products.index:
            product_name = products_df.loc[
                products_df["product_id"] == pid, "product_name"
            ].values[0]
            result.append(f"{product_name} ({top_products[pid]} sold)")
        response_text = "Top 5 most sold products:\n" + "\n".join(result)

    # ✅ 2. Stock check for a specific product
    elif "stock" in user_message or "left" in user_message:
        found = False
        for _, row in products_df.iterrows():
            if row["product_name"].lower() in user_message:
                pid = row["product_id"]
                # Count available items in inventory (not sold yet)
                stock_left = inventory_df[
                    (inventory_df["product_id"] == pid) & (inventory_df["sold_at"].isna())
                ].shape[0]
                response_text = (
                    f"{row['product_name']} has {stock_left} items left in stock."
                )
                found = True
                break
        if not found:
            response_text = "Sorry, I couldn't find that product in stock."

    # ✅ Save conversation
    sessions[session_id]["messages"].append({"user": user_message, "bot": response_text})

    return jsonify({"response": response_text})


if __name__ == "__main__":
    app.run(debug=False)
