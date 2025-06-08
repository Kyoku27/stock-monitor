from flask import Flask, request, jsonify
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
