import os
import csv
import io
import json
import requests
import pandas as pd

# ✅ 获取品牌对应的库存表链接（由环境变量提供）
def get_sheet_csv_url_by_brand(brand):
    return {
        "HRP": os.getenv("SHEET_HRP_URL"),
        "CZUR": os.getenv("SHEET_CZUR_URL")
    }.get(brand)

# ✅ 读取 MOFT 品牌多个表的库存（适配多个 URL）
def get_moft_stock_from_multiple_csvs(target_sku):
    urls = json.loads(os.environ.get("SHEET_MOFT_URLS", "[]"))
    for url in urls:
        try:
            res = requests.get(url)
            content = res.content.decode("utf-8")
            df = pd.read_csv(io.StringIO(content), header=None)
            for col in df.columns:
                if str(df.iloc[3, col]).strip() == target_sku:
                    return str(df.iloc[7, col]).strip()  # ✅ 第8行是「今月」库存
        except Exception as e:
            print(f"[ERROR] MOFT Sheet error: {e}")
    return None

# ✅ 主函数：根据「型番」+ 品牌 查库存（第4行找列名 -> 第8行找值）
def get_real_stock_by_sku(sku, brand):
    if brand == "MOFT":
        stock = get_moft_stock_from_multiple_csvs(sku)
        return {"商品ID": sku, "在庫": stock} if stock else {}

    url = get_sheet_csv_url_by_brand(brand)
    if not url:
        return {}

    try:
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

        stock_row = rows[7]  # 第8行 = 今月在庫

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

    except Exception as e:
        print(f"[ERROR] Google Sheet Fetch Failed: {e}")
        return {}

# ✅ 映射表读取函数（你用 Google Sheet CSV 导出的 link）
def get_brand_and_sku_map():
    url = os.getenv("GOOGLE_SHEET_CSV_URL")
    try:
        res = requests.get(url)
        res.raise_for_status()
        content = res.content.decode("utf-8-sig")  # ← 强制去除BOM + utf-8读取
        df = pd.read_csv(io.StringIO(content))

        # 标准化字段名（去除前后空格 + 中文/日文正常显示）
        df.columns = df.columns.str.strip()

        print("[DEBUG] 映射表字段：", df.columns.tolist())  # 可删除

        return df.to_dict(orient="records")
    except Exception as e:
        print(f"[ERROR] SKU mapping fetch failed: {e}")
        return []



