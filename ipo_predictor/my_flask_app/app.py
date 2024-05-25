from flask import Flask, jsonify, render_template
from flask_restful import Api, Resource
from data_fetcher import fetch_stock_data, fetch_disclosure_data

app = Flask(__name__)
api = Api(app)

class StockData(Resource):
    def get(self):
        data = fetch_stock_data('AAPL')
        return jsonify(data)

class DisclosureData(Resource):
    def get(self):
        data = fetch_disclosure_data()
        return jsonify(data)

api.add_resource(StockData, '/api/stock_data')  # /api/stock_data に修正
api.add_resource(DisclosureData, '/api/disclosure_data')  # /api/disclosure_data に修正

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)

