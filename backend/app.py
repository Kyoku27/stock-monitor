import os
import csv
import io
import requests
from flask import Flask, request, jsonify

from rakuten_api import get_rakuten_inventory
from gsheet_api import (
    get_moft_stock_from_multiple_csvs,
    get_brand_and_sku_map,
    get_real_stock_by_sku
)

app = Flask(__name__, static_folder="../frontend", static_url_path="")

SHEET_CSV_URL = os.environ.get("GOOGLE_SHEET_CSV_URL", "")

# -----------------------------
# ✅ Google Sheets：根据 SKU（型番）查库存
@app.route("/api/stock/gsheet")
def gsheet_stock():
    query = request.args.get("sku", "").strip()
    if not query:
        return jsonify({"error": "Missing SKU"}), 400

    mapping = get_brand_and_sku_map()
    match = next((row for row in mapping if query == row.get("システム連携用SKU番号", "")), None)
    if not match:
        return jsonify({"error": "SKU not found"}), 404

    型番 = match.get("型番", "").strip()
    brand = match.get("ブランド", "").strip()

    try:
        stock_data = get_real_stock_by_sku(型番, brand)
    except Exception as e:
        print(f"[ERROR] GSheet failed: {e}")
        stock_data = {}

    return jsonify({
        "ブランド": brand,
        "型番": 型番,
        "在庫": stock_data
    })

# -----------------------------
# ✅ 乐天库存查询：使用 SKU管理番号 + SKU 番号
@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    data = get_rakuten_inventory(manage_number, sku_list)
    return jsonify(data)

# -----------------------------
# ✅ 获取 SKU 映射表（初始化搜索用）
@app.route("/api/stock/mapping")
def stock_mapping():
    if not SHEET_CSV_URL:
        return jsonify({"error": "GOOGLE_SHEET_CSV_URL not set"}), 500

    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
    except Exception as e:
        return jsonify({"error": f"Google Sheet CSV fetch failed: {str(e)}"}), 500

    f = io.StringIO(response.text)
    reader = csv.DictReader(f)
    data = [row for row in reader if any(row.values())]
    return jsonify(data)

# -----------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

