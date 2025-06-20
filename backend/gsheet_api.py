import os
import csv
import io
import requests
from flask import Flask, request, jsonify

from rakuten_api import get_rakuten_inventory
from gsheet_api import get_real_stock_by_sku
from gsheet_mapping import get_brand_and_sku_map

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# -----------------------------
@app.route("/api/stock/real")
def real_stock():
    query = request.args.get("sku", "").strip()
    if not query:
        return jsonify({"error": "Missing SKU"}), 400

    mapping = get_brand_and_sku_map()
    match = next((row for row in mapping if query == row.get("システム連携用SKU番号", "")), None)
    if not match:
        return jsonify({"error": "SKU not found"}), 404

    brand = match.get("ブランド", "")
    型番 = match.get("型番", "")
    manage_number = match.get("SKU管理番号", "")

    # ✅ 乐天库存查询（按 SKU管理番号 和 query 作为 variantId）
    rakuten_quantity = "-"
    try:
        rakuten_data = get_rakuten_inventory(manage_number, [query])
        for item in rakuten_data:
            if item.get("variantId") == query:
                rakuten_quantity = item.get("quantity", "-")
                break
    except Exception as e:
        print(f"[ERROR] 楽天 API 失败: {e}")

    # ✅ Google Sheet 库存（按 型番 查）
    google_stock = {}
    try:
        google_stock = get_real_stock_by_sku(型番, brand)
    except Exception as e:
        print(f"[ERROR] Google Sheet 库存获取失败: {e}")

    return jsonify({
        "ブランド": brand,
        "SKU": query,
        "楽天在庫": rakuten_quantity,
        "在庫": google_stock
    })

# -----------------------------
@app.route("/api/stock/mapping")
def stock_mapping():
    try:
        mapping = get_brand_and_sku_map()
        return jsonify(mapping)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# -----------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
