# Flask main app
from flask import Flask, jsonify
app = Flask(__name__)

@app.route('/')
def home():
    return 'Stock Monitor Backend Running'

if __name__ == '__main__':
    app.run(debug=True)