import os
import json
from flask import Flask, request, jsonify
from rakuten_api import get_rakuten_inventory
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# ✅ 允许 Flask 正确找到 frontend 静态文件
app = Flask(__name__, static_folder="../frontend", static_url_path="")

# -----------------------------
# Google Sheets 从环境变量读取库存
# -----------------------------
def get_google_inventory(sku_list):
    service_account_info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1nmQc-OJB3crXRzTjPwRcfaXjuTJVXCoLQPn0AeM6SrA")
    SHEET_NAME = os.environ.get("GOOGLE_SHEET_SHEETNAME", "楽天")
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    rows = sheet.get_all_records()

    sku_to_stock = {}
    for row in rows:
        sku_key = row.get("システム連携用SKU番号", "").strip()
        if sku_key in sku_list:
            sku_to_stock[sku_key] = row.get("在庫", 0)
    return sku_to_stock

# -----------------------------
# ✅ 新接口：返回整张映射表（含SKU, 品名, 品牌等）
# -----------------------------
@app.route("/api/stock/mapping")
def stock_mapping():
    service_account_info = json.loads(os.environ.get("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
    client = gspread.authorize(creds)

    SHEET_ID = os.environ.get("GOOGLE_SHEET_ID", "1nmQc-OJB3crXRzTjPwRcfaXjuTJVXCoLQPn0AeM6SrA")
    SHEET_NAME = os.environ.get("GOOGLE_SHEET_SHEETNAME", "楽天")
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    rows = sheet.get_all_records()

    return jsonify(rows)

# -----------------------------
# API 路由：返回库存数据
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
# 首页和静态文件托管
# -----------------------------
@app.route("/")
def index():
    return app.send_static_file("index.html")

# -----------------------------
# 启动应用
# -----------------------------
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)





