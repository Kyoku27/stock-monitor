def get_google_inventory(sku_list):
    fake_data = {
        "CZR001": 10,
        "CZR002": 8,
        "CZR003": 0
    }
    return {sku: fake_data.get(sku, 0) for sku in sku_list}
# Placeholder for Google Sheet API integration
