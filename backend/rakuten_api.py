import random

# 示例：获取 SKU 库存数量（假设数据来自 API 或数据库）
def get_rakuten_inventory(sku_list):
    result = []
    for sku in sku_list:
        # 这里是假数据，可以替换为实际对 Rakuten RMS API 的调用
        result.append({
            "sku": sku,
            "stock": random.randint(0, 100)  # 随机生成库存数
        })
    return result

