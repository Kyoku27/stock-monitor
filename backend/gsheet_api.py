import gspread
from oauth2client.service_account import ServiceAccountCredentials

SHEET_ID = "1nmQc-OJB3crXRzTjPwRcfaXjuTJVXCoLQPn0AeM6SrA"
SHEET_NAME = "楽天"

scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)

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
