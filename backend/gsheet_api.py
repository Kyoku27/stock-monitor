# ✅ backend/gsheet_stock.py
import os
import csv
import io
import json
import requests
import pandas as pd

# ✅ 获取库存表链接

def get_sheet_csv_url_by_brand(brand):
    return {
        "HRP": os.getenv("SHEET_HRP_URL"),
        "CZUR": os.getenv("SHEET_CZUR_URL")
    }.get(brand)

# ✅ 自动查找 MOFT 所在的表格（遍历）
def get_moft_stock_from_multiple_csvs(target_sku):
    urls = json.loads(os.environ.get("SHEET_MOFT_URLS", "[]"))

    for url in urls:
        try:
            response = requests.get(url)
            content = response.content.decode("utf-8")
            df = pd.read_csv(io.StringIO(content), header=None)

            for col in df.columns:
                if str(df.iloc[3, col]).strip() == target_sku:
                    return str(df.iloc[7, col]).strip()
        except Exception as e:
            print(f"[ERROR] Failed to fetch from {url}: {e}")

    return None


def get_real_stock_by_sku(sku, brand):
    if brand == "MOFT":
        stock = get_moft_stock_from_multiple_csvs(sku)
        return {"在庫": stock} if stock else {}

    url = get_sheet_csv_url_by_brand(brand)
    if not url:
        return {}

    res = requests.get(url)
    res.raise_for_status()
    rows = list(csv.reader(io.StringIO(res.text)))

    target_col = -1
    for idx, val in enumerate(rows[3]):
        if val.strip() == sku:
            target_col = idx
            break

    if target_col == -1:
        return {}

    stock_row = rows[5]

    if brand == "HRP":
        return {
            "自社": stock_row[target_col].strip(),
            "City": stock_row[target_col + 1].strip() if target_col + 1 < len(stock_row) else ""
        }
    else:
        return {
            "在庫": stock_row[target_col].strip()
        }


# ✅ backend/gsheet_mapping.py
import os
import csv
import io
import requests

MAPPING_CSV_URL = os.getenv("GOOGLE_SHEET_CSV_URL")

def get_brand_and_sku_map():
    res = requests.get(MAPPING_CSV_URL)
    res.raise_for_status()
    rows = csv.DictReader(io.StringIO(res.text))
    result = []
    for row in rows:
        result.append({
            "型番": row.get("型番", "").strip(),
            "ブランド": row.get("ブランド", "").strip(),
            "システム連携用SKU番号": row.get("システム連携用SKU番号", "").strip()
        })
    return result


# ✅ app.py - 添加新接口
from gsheet_mapping import get_brand_and_sku_map
from gsheet_stock import get_real_stock_by_sku

@app.route("/api/stock/real")
def real_stock():
    query = request.args.get("sku", "").strip()
    if not query:
        return jsonify({"error": "Missing SKU"}), 400

    mapping = get_brand_and_sku_map()
    match = next((row for row in mapping if row["型番"] == query), None)
    if not match:
        return jsonify({"error": "SKU not found"}), 404

    brand = match["ブランド"]
    sku = match["型番"]
    stock_data = get_real_stock_by_sku(sku, brand)

    return jsonify({
        "ブランド": brand,
        "型番": sku,
        "在庫": stock_data
    })


