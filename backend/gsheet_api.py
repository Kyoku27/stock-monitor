import os
import json
import gspread
from oauth2client.service_account import ServiceAccountCredentials

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

# 从环境变量读取服务账户 JSON 内容
service_account_info = json.loads(os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "{}"))
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
SHEET_NAME = os.getenv("GOOGLE_SHEET_SHEETNAME", "楽天")

def get_google_stock_mapping():
    sheet = client.open_by_key(SHEET_ID).worksheet(SHEET_NAME)
    rows = sheet.get_all_records()
    results = []
    for row in rows:
        results.append({
            "SKU管理番号": row.get("SKU管理番号"),
            "システム連携用SKU番号": row.get("システム連携用SKU番号"),
            "型番": row.get("型番"),
            "ブランド": row.get("ブランド"),
            "商品ID": row.get("商品ID"),
            "在庫": row.get("在庫", "")
        })
    return results

