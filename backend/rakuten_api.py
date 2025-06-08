import os
import requests
import base64

def get_rakuten_inventory(sku_list):
    service_secret = os.getenv("RAKUTEN_SERVICE_SECRET")
    license_key = os.getenv("RAKUTEN_LICENSE_KEY")

    headers = {
        "Authorization": "ESA " + base64.b64encode(f"{service_secret}:{license_key}".encode()).decode(),
        "Content-Type": "application/json"
    }

    results = []
    for sku in sku_list:
        # 实际上你还需要知道商品管理番号（manageNumber），假设为 "MNG123"
        url = f"https://api.rms.rakuten.co.jp/es/2.0/inventories/manage-numbers/MNG123/variants/{sku}"

        res = requests.get(url, headers=headers)
        if res.status_code == 200:
            results.append(res.json())
        else:
            results.append({"sku": sku, "error": res.status_code, "message": res.text})

    return results

