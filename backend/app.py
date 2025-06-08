import os
from flask import Flask, request, jsonify, send_from_directory
from rakuten_api import get_rakuten_inventory

app = Flask(__name__, static_folder="../frontend")

# API 接口
@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    data = get_rakuten_inventory(manage_number, sku_list)
    return jsonify(data)

# 前端首页
@app.route("/")
def serve_index():
    return send_from_directory(app.static_folder, "index.html")

# 前端静态资源（script.js / style.css 等）
@app.route("/<path:filename>")
def serve_static(filename):
    return send_from_directory(app.static_folder, filename)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)


