import os
from flask import Flask, request, jsonify, send_from_directory
from rakuten_api import get_rakuten_inventory

app = Flask(
    __name__,
    static_folder="../frontend",        # 指定前端路径（根据你的项目结构）
    static_url_path=""                  # 让 CSS/JS 可从根路径引用
)

# ✅ API 接口：获取乐天库存数据
@app.route("/api/stock/rakuten")
def rakuten_stock():
    manage_number = request.args.get("manage")
    sku_list = request.args.getlist("sku")

    if not manage_number or not sku_list:
        return jsonify({"error": "Please provide manage and SKU(s) via ?manage=XXX&sku=SKU1&sku=SKU2"}), 400

    data = get_rakuten_inventory(manage_number, sku_list)
    return jsonify(data)

# ✅ 返回前端页面
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

# ✅ 返回静态资源（JS、CSS）
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

# ✅ 启动服务
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)




