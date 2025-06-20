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
            "SKU管理番号": row.get("SKU管理番号", "").strip(),
            "型番": row.get("型番", "").strip(),
            "ブランド": row.get("ブランド", "").strip(),
            "システム連携用SKU番号": row.get("システム連携用SKU番号", "").strip()
        })
    return result

