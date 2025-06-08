from flask import Flask, request, jsonify
from rakuten_api import get_rakuten_inventory  # ✅ 不要加 backend.

app = Flask(__name__)

@app.route("/api/stock/rakuten")
def rakuten_stock():
    sku_list = request.args.getlist("sku")
    if not sku_list:
        return jsonify({"error": "Please provide SKU(s) via ?sku=SKU1&sku=SKU2"}), 400
    data = get_rakuten_inventory(sku_list)
    return jsonify(data)

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))  # Render 自动注入的端口
    app.run(host="0.0.0.0", port=port)
