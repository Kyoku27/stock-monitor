import os
from flask import Flask, request, jsonify, send_from_directory
from rakuten_api import get_rakuten_inventory

app = Flask(__name__)

@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    data = get_rakuten_inventory(manage_number, sku_list)
    return jsonify(data)

# ✅ 加载前端 index.html 页面
@app.route("/")
def frontend():
    return send_from_directory("frontend", "index.html")

# ✅ 加载 static js/css 文件
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("frontend", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)



