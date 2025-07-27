from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import requests
import re

app = Flask(__name__)
CORS(app)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
products_df    = pd.read_csv(os.path.join(DATA_DIR, "products.csv"))
order_items_df = pd.read_csv(os.path.join(DATA_DIR, "order_items.csv"))
orders_df      = pd.read_csv(os.path.join(DATA_DIR, "orders.csv"))
inventory_df   = pd.read_csv(os.path.join(DATA_DIR, "inventory_items.csv"))

products_df = products_df.rename(columns={"id": "product_id", "name": "product_name"})

sessions = {}
session_counter = 1

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"

def ask_groq(prompt: str) -> str:
    if not GROQ_API_KEY:
        return "LLM key not configured."
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "system", "content": "You are an e-commerce assistant."},
                     {"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    resp = requests.post(GROQ_API_URL, json=payload, headers=headers)
    if resp.status_code == 200:
        return resp.json()["choices"][0]["message"]["content"]
    return f"LLM error ({resp.status_code}): {resp.text}"

@app.route("/sessions", methods=["POST"])
def create_session():
    global session_counter
    user_id = request.json.get("user_id")
    sid = session_counter
    sessions[sid] = {"user_id": user_id, "messages": []}
    session_counter += 1
    return jsonify({"session_id": sid}), 201

@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json()
    sid  = data.get("session_id")
    msg  = data.get("message", "")

    if sid not in sessions:
        return jsonify({"response": "Invalid session ID"}), 400

    text = msg.lower()
    response = "Sorry, I don't understand your question."

    if "top" in text and "sold" in text:
        top5 = (order_items_df
                .groupby("product_id")["id"]
                .count()
                .sort_values(ascending=False)
                .head(5))
        lines = []
        for pid, cnt in top5.items():
            name = products_df.loc[products_df["product_id"] == pid, "product_name"].iloc[0]
            lines.append(f"{name}: {cnt}")
        response = "Top 5 most sold products:\n" + "\n".join(lines)

    elif "status of order id" in text or "order status" in text:
        m = re.search(r"order\s+id\s+(\d+)", text)
        if m:
            oid = int(m.group(1))
            row = orders_df.loc[orders_df["order_id"] == oid]
            if not row.empty:
                status = row.iloc[0]["status"]
                response = f"Order {oid} is currently '{status}'."
            else:
                response = f"No order found with ID {oid}."
        else:
            response = "Please specify a valid order ID, e.g. 12345."

    elif "stock" in text or "left" in text:
        found = False
        for _, prod in products_df.iterrows():
            pname = prod["product_name"].lower()
            if pname in text:
                pid = prod["product_id"]
                left = inventory_df[
                    (inventory_df["product_id"] == pid) &
                    (inventory_df["sold_at"].isna())
                ].shape[0]
                response = f"{prod['product_name']} has {left} items left in stock."
                found = True
                break
        if not found:
            response = "Sorry, I couldn't find that product in stock."

    else:
        response = ask_groq(msg)

    sessions[sid]["messages"].append({"user": msg, "bot": response})
    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
