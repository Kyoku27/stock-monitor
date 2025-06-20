import os
import csv
import io
import json
import requests
import pandas as pd

# ✅ 映射表：SKU ↔ 型番 ↔ 品牌 ↔ 管理番号
def get_brand_and_sku_map():
    MAPPING_CSV_URL = os.getenv("GOOGLE_SHEET_CSV_URL")
    if not MAPPING_CSV_URL:
        print("[ERROR] Missing GOOGLE_SHEET_CSV_URL env")
        return []

    try:
        res = requests.get(MAPPING_CSV_URL)
        res.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Mapping fetch failed: {e}")
        return []

    rows = csv.DictReader(io.StringIO(res.text))
    result = []
    for row in rows:
        result.append({
            "SKU管理番号": row.get("SKU管理番号", "").strip(),
            "型番": row.get("型番", "").strip(),
            "ブランド": row.get("ブランド", "").strip(),
            "システム連携用SKU番号": row.get("システム連携用SKU番号", "").strip()
        })
    return result


# ✅ 获取品牌 → 对应 Google Sheet 链接
def get_sheet_csv_url_by_brand(brand):
    return {
        "HRP": os.getenv("SHEET_HRP_URL"),
        "CZUR": os.getenv("SHEET_CZUR_URL")
    }.get(brand)


# ✅ MOFT：遍历多个表查库存
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


# ✅ 主函数：根据型番 + 品牌查库存
def get_real_stock_by_sku(sku, brand):
    if brand == "MOFT":
        stock = get_moft_stock_from_multiple_csvs(sku)
        return {"商品ID": sku, "在庫": stock} if stock else {}

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

    stock_row = rows[7]

    if brand == "HRP":
        return {
            "商品ID": sku,
            "自社": stock_row[target_col].strip(),
            "City": stock_row[target_col + 1].strip() if target_col + 1 < len(stock_row) else ""
        }
    else:
        return {
            "商品ID": sku,
            "在庫": stock_row[target_col].strip()
        }


