from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_total_gain(stocks):
    total_gain = 0
    for stock in stocks:
        current_value = float(stock['stock value'])
        purchase_price = float(stock['purchase_price'])
        gain = current_value - purchase_price
        total_gain += gain
    return total_gain



@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    filters = request.args.to_dict()
    stocks1_url = 'http://stocks1-a:8000/stocks'
    stocks2_url = 'http://stocks2:8000/stocks'

    try:
        if filters:
           stocks1_url += "?"
           stocks1_url += '&'.join([f"{key}={value}" for key, value in filters.items()])

        if filters:
           stocks2_url += "?"
           stocks2_url += '&'.join([f"{key}={value}" for key, value in filters.items()])
        stocks1 = requests.get(stocks1_url).json()
        stocks2 = requests.get(stocks2_url).json()
    except requests.exceptions.ConnectionError:
      return jsonify({'error':'Could not connect to stocks services'}), 500
    all_stocks = stocks1 + stocks2
    total_gain = get_total_gain(all_stocks)
    return jsonify(total_gain)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)