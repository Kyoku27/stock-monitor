import os
from flask import Flask, request, jsonify, send_from_directory
from rakuten_api import get_rakuten_inventory
from gsheet_api import get_google_inventory

app = Flask(__name__)

@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    rakuten_data = get_rakuten_inventory(manage_number, sku_list)
    google_data = get_google_inventory(sku_list)

    merged = []
    for item in rakuten_data:
        sku = item.get("variantId")
        merged.append({
            "sku": sku,
            "rakuten": item.get("quantity"),
            "google": google_data.get(sku, 0),
        })
    return jsonify(merged)

@app.route("/")
def frontend():
    return send_from_directory("frontend", "index.html")

@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory("frontend", path)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




