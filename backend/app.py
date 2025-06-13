import os
import csv
import io
import requests
from flask import Flask, request, jsonify
from rakuten_api import get_rakuten_inventory

# ✅ 前端托管设置
app = Flask(__name__, static_folder="../frontend", static_url_path="")

# ✅ 公共 Google Sheet CSV 地址（楽天映射表）
SHEET_CSV_URL = "https://docs.google.com/spreadsheets/d/1nmQc-OJB3crXRzTjPwRcfaXjuTJVXCoLQPn0AeM6SrA/gviz/tq?tqx=out:csv&sheet=楽天"

# -----------------------------
# ✅ 函数：从共享 CSV 获取 Google Sheets 在庫
# -----------------------------
def get_google_inventory(sku_list):
    try:
        response = requests.get(SHEET_CSV_URL)
        response.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Google Sheet fetch failed: {str(e)}")
        return {}

    f = io.StringIO(response.text)
    reader = csv.DictReader(f)
    stock_map = {}
    for row in reader:
        sku = row.get("システム連携用SKU番号", "").strip()
        if sku in sku_list:
            try:
                stock_map[sku] = int(row.get("在庫", 0))
            except:
                stock_map[sku] = 0
    return stock_map

# -----------------------------
# ✅ 接口1：获取整张 SKU 映射表（用于前端初始化）
# -----------------------------
@app.route("/api/stock/mapping")
def stock_mapping():
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
# ✅ 接口2：获取楽天 + Google在庫（合并）
# -----------------------------
@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    rakuten_data = get_rakuten_inventory(manage_number, sku_list)
    google_data = get_google_inventory(sku_list)

    merged = []
    for item in rakuten_data:
        sku = item.get("variantId")
        merged.append({
            "sku": sku,
            "rakuten": item.get("quantity"),
            "google": google_data.get(sku, 0),
        })
    return jsonify(merged)

# -----------------------------
# ✅ 首页：返回 index.html
# -----------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# -----------------------------
# ✅ 启动应用
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)






