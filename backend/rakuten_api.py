import requests
import xml.etree.ElementTree as ET
import os

# ✅ 乐天库存 API
RAKUTEN_ENDPOINT = "https://api.rms.rakuten.co.jp/es/2.0/order/getInventoryExternal"

# ✅ 获取授权信息（从环境变量）
SERVICE_SECRET = os.environ.get("RAKUTEN_SERVICE_SECRET")
LICENSE_KEY = os.environ.get("RAKUTEN_LICENSE_KEY")

# ✅ 构建请求 Header
HEADERS = {
    "Content-Type": "application/xml",
    "Authorization": f"ESA {SERVICE_SECRET}:{LICENSE_KEY}"
}

# ✅ 调用乐天 RMS 查询库存
def get_rakuten_inventory(manage_number, sku_list):
    body = f"""
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ns1="http://inventory.external.rms.rakuten.co.jp/">
  <soapenv:Header/>
  <soapenv:Body>
    <ns1:getInventoryExternalRequest>
      <itemInventorySearchModel>
        <itemInventorySearchType>1</itemInventorySearchType>
        <itemInventorySearchKeyword>{manage_number}</itemInventorySearchKeyword>
      </itemInventorySearchModel>
    </ns1:getInventoryExternalRequest>
  </soapenv:Body>
</soapenv:Envelope>
""".strip()

    try:
        response = requests.post(RAKUTEN_ENDPOINT, headers=HEADERS, data=body.encode("utf-8"))
        response.raise_for_status()

        root = ET.fromstring(response.text)
        results = []

        for item in root.findall(".//itemInventory"):
            variant_id = item.findtext("inventoryTypeChildNo") or ""
            quantity = item.findtext("inventoryQuantity") or "0"

            if variant_id in sku_list:
                results.append({
                    "variantId": variant_id,
                    "quantity": quantity
                })

        return results
    except Exception as e:
        print(f"[ERROR] Rakuten API failed: {e}")
        return []


