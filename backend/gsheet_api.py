# ✅ backend/gsheet_stock.py
import os
import csv
import io
import requests

# ✅ 不暴露任何链接在代码中，均来自环境变量
def get_sheet_csv_url(sku, brand):
    if brand == "HRP":
        return os.getenv("SHEET_HRP_URL")
    elif brand == "CZUR":
        return os.getenv("SHEET_CZUR_URL")
    elif brand == "MOFT":
        moft_map = json.loads(os.getenv("SHEET_MOFT_MAP_JSON", "{}"))
        return moft_map.get(sku)
    else:
        return None


def get_real_stock_by_sku(sku, brand):
    url = get_sheet_csv_url_by_brand(brand)
    if not url:
        return {}

    res = requests.get(url)
    res.raise_for_status()
    rows = list(csv.reader(io.StringIO(res.text)))

    # 找型番的列号（在第4行）
    target_col = -1
    for idx, val in enumerate(rows[3]):
        if val.strip() == sku:
            target_col = idx
            break

    if target_col == -1:
        return {}

    stock_row = rows[5]  # 第6行是 "今月" 在庫

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


