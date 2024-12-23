from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Get the total gain of the stocks by calling the stock1 and stock2 services api
def get_total_gain(stocks):
    total_gain = 0
    for stock in stocks:
      stock_value_url = 'http://stocks1:8000/stock-value/{}'.format(stock['_id'])

      try:
        stock_value = requests.get(stock_value_url).json()
        current_value = float(stock_value['stock value'])
        purchase_price = float(stock['purchase price'])
        gain = current_value - purchase_price
        total_gain += gain
      except requests.exceptions.ConnectionError:
         print("Error when getting stock value: ",stock_value_url)
    return total_gain

# Filters using the query parameters
def filter_stocks(stocks, filters):
  filtered_stocks = []
  for stock in stocks:
    match = True
    if 'portfolio' in filters:
        match = match and stock['_id'].startswith(filters['portfolio'])
    if 'numsharesgt' in filters:
        match = match and float(stock['shares']) > float(filters['numsharesgt'])
    if 'numshareslt' in filters:
        match = match and float(stock['shares']) < float(filters['numshareslt'])
    if match:
      filtered_stocks.append(stock)
  return filtered_stocks

# GET /capital-gains
@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    filters = request.args.to_dict()

    stocks1_url = 'http://stocks1:8000/stocks'
    stocks2_url = 'http://stocks2:8000/stocks'

    try:
        stocks1 = requests.get(stocks1_url).json()
        stocks2 = requests.get(stocks2_url).json()
    except requests.exceptions.ConnectionError:
      return jsonify({'error':'Could not connect to stocks services'}), 500
    all_stocks = stocks1 + stocks2
    filtered_stocks = filter_stocks(all_stocks, filters)

    total_gain = get_total_gain(filtered_stocks)
    return jsonify(total_gain)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)