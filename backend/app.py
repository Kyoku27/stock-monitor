import os
from flask import Flask, request, jsonify, send_from_directory
from rakuten_api import get_rakuten_inventory
from gsheet_api import (
    get_brand_and_sku_map,
    get_real_stock_by_sku,
)

app = Flask(__name__, static_folder="../frontend", static_url_path="")

# -----------------------------
# ✅ 首页（静态 index.html）
# -----------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# -----------------------------
# ✅ SKU映射表：从 Google Sheet 映射表 CSV 读取
# -----------------------------
@app.route("/api/stock/mapping")
def stock_mapping():
    try:
        data = get_brand_and_sku_map()
        return jsonify(data)
    except Exception as e:
        return jsonify({"error": f"Mapping fetch failed: {str(e)}"}), 500

# -----------------------------
# ✅ 在庫查询（统一接口）：通过 SKU查询 Google 表 + 乐天
# -----------------------------
@app.route("/api/stock/real")
def real_stock():
    query = request.args.get("sku", "").strip()
    if not query:
        return jsonify({"error": "Missing SKU"}), 400

    mapping = get_brand_and_sku_map()
    match = next((row for row in mapping if query in (
        row.get("システム連携用SKU番号", ""),
        row.get("型番", ""),
        row.get("SKU管理番号", "")
    )), None)

    if not match:
        return jsonify({"error": "SKU not found"}), 404

    sku_for_api = match.get("システム連携用SKU番号", "").strip()
    型番 = match.get("型番", "").strip()
    brand = match.get("ブランド", "").strip()
    manage_number = match.get("SKU管理番号", "").strip()

    # 🎯 乐天库存：SKU管理番号 + SKU 番号查询
    rakuten_quantity = "-"
    try:
        rakuten_data = get_rakuten_inventory(manage_number, [sku_for_api])
        for item in rakuten_data:
            if item.get("variantId") == sku_for_api:
                rakuten_quantity = item.get("quantity", "-")
                break
    except Exception as e:
        print(f"[ERROR] 楽天API failed: {e}")

    # 🎯 Google Sheet 查询
    try:
        stock_data = get_real_stock_by_sku(型番, brand)
    except Exception as e:
        print(f"[ERROR] Google Sheet fetch failed: {e}")
        stock_data = {}

    return jsonify({
        "ブランド": brand,
        "型番": 型番,
        "楽天在庫": rakuten_quantity,
        "在庫": stock_data
    })

# -----------------------------
# ✅ 启动服务
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)

