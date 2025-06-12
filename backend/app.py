from flask import Flask, request, jsonify, send_from_directory
from rakuten_api import get_rakuten_inventory
from gsheet_api import get_google_stock_mapping
import os

app = Flask(__name__)

@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    rakuten_data = get_rakuten_inventory(manage_number, sku_list)
    sheet_mapping = get_google_stock_mapping()

    combined = []
    for row in rakuten_data:
        sku = row.get("variantId")
        mapped = next((item for item in sheet_mapping if item['システム連携用SKU番号'] == sku), {})
        combined.append({
            "sku": sku,
            "rakuten_stock": row.get("quantity"),
            "google_stock": mapped.get("在庫", "-"),
            "brand": mapped.get("ブランド", ""),
            "type": mapped.get("型番", "")
        })

    return jsonify(combined)

@app.route("/")
def index():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("frontend", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




