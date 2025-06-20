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

# ✅ 设置 Flask 应用并指定前端文件夹
app = Flask(__name__, static_folder="../frontend", static_url_path="")

# ✅ 映射表 CSV（初始化表）
SHEET_CSV_URL = os.environ.get("GOOGLE_SHEET_CSV_URL", "")

# -----------------------------
# ✅ 函数：从映射表中读取 Google 在庫（用于 /api/stock/rakuten）
# -----------------------------
def get_google_inventory(sku_list):
    if not SHEET_CSV_URL:
        print("[ERROR] SHEET_CSV_URL not set")
        return {}

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
# ✅ 接口 1：获取 SKU 映射表（初始化用）
# -----------------------------
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
# ✅ 接口 2：楽天 + Google 在庫合并返回
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
# ✅ 接口 3：MOFT 实时库存（从多个表中找）
# -----------------------------
@app.route("/api/stock/moft")
def stock_moft():
    sku = request.args.get("sku")
    if not sku:
        return jsonify({"error": "SKU is required"}), 400

    stock = get_moft_stock_from_multiple_csvs(sku)
    if stock is None:
        return jsonify({"sku": sku, "status": "not_found"})
    else:
        return jsonify({"sku": sku, "stock": stock})

# -----------------------------
# ✅ 接口 4：统一查询 SKU → 实时读取实际库存（HRP, CZUR, MOFT 通用）
# -----------------------------
@app.route("/api/stock/real")
def real_stock():
    query = request.args.get("sku", "").strip()
    if not query:
        return jsonify({"error": "Missing SKU"}), 400

    mapping = get_brand_and_sku_map()

    match = next(
        (row for row in mapping if query in (
            row.get("SKU管理番号", ""),
            row.get("型番", ""),
            row.get("システム連携用SKU番号", "")
        )),
        None
    )

    if not match:
        return jsonify({"error": "SKU not found"}), 404

    brand = match.get("ブランド", "")
    sku = match.get("型番", "")
    stock_data = get_real_stock_by_sku(sku, brand)

    return jsonify({
        "ブランド": brand,
        "型番": sku,
        "在庫": stock_data
    })

# -----------------------------
# ✅ 首页页面（index.html）
# -----------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# -----------------------------
# ✅ 启动服务
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
