from flask import Flask, request, jsonify
from flask_cors import CORS
import pandas as pd
import os
import requests
import sqlite3


app = Flask(__name__)
CORS(app)

DB_PATH = os.path.join(os.path.dirname(__file__), "instance", "ecommerce.db")

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")

# ----------------------------
# ✅ Groq LLM Setup
# ----------------------------
GROQ_API_KEY = "API_KEY_HERE"  # Replace with your actual Groq API key
GROQ_API_URL = "URL-here"

def ask_groq_llm(prompt):
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": "mixtral-8x7b-32768",
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 0.2
    }
    try:
        response = requests.post(GROQ_API_URL, json=payload, headers=headers)
        if response.status_code == 200:
            return response.json()["choices"][0]["message"]["content"]
        else:
            return f"Groq API Error: {response.text}"
    except Exception as e:
        return f"Groq API Connection Failed: {str(e)}"

# ----------------------------
# ✅ Load CSVs into SQLite
# ----------------------------
def load_csvs_into_sqlite():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)

    csv_files = {
        "distribution_centers": "distribution_centers.csv",
        "inventory_items": "inventory_items.csv",
        "order_items": "order_items.csv",
        "orders": "orders.csv",
        "products": "products.csv",
        "users": "users.csv",
    }

    for table, csv_file in csv_files.items():
        df = pd.read_csv(os.path.join(DATA_DIR, csv_file))
        df.to_sql(table, conn, if_exists="replace", index=False)
        print(f"Loaded {csv_file} into table {table}")

    conn.close()

# Load data at startup
load_csvs_into_sqlite()

# ----------------------------
# ✅ Helper Query Functions
# ----------------------------
def get_top_sold_products(limit=5):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT p.name, COUNT(o.id) as sales
        FROM order_items o
        JOIN products p ON o.product_id = p.id
        GROUP BY p.name
        ORDER BY sales DESC
        LIMIT ?
    """
    df = pd.read_sql_query(query, conn, params=(limit,))
    conn.close()
    return df.to_dict(orient="records")

def get_stock_left(product_name):
    conn = sqlite3.connect(DB_PATH)
    query = """
        SELECT COUNT(*) as stock
        FROM inventory_items
        WHERE product_name LIKE ? AND sold_at IS NULL
    """
    df = pd.read_sql_query(query, conn, params=(f"%{product_name}%",))
    conn.close()
    return df["stock"][0]


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
    message = data.get("message", "")

    if session_id not in sessions:
        return jsonify({"response": "Invalid session ID"}), 400

    response_text = "Sorry, I don't understand your question."

    
    if "top" in message.lower() and "sold" in message.lower():
        products = get_top_sold_products()
        response_text = "Top sold products:\n" + "\n".join(
            [f"{p['name']} ({p['sales']} sold)" for p in products]
        )

    
    elif "stock" in message.lower() or "left" in message.lower():
        words = message.split()
        product_name = None
        for word in words:
            if len(word) > 3:  # crude match, you can improve with NLP
                product_name = word
                break
        if product_name:
            stock = get_stock_left(product_name)
            response_text = f"{stock} {product_name} left in stock."
        else:
            response_text = "Please specify the product name."

  
    else:
        response_text = ask_groq_llm(message)

    sessions[session_id]["messages"].append({"user": message, "bot": response_text})
    return jsonify({"response": response_text})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
