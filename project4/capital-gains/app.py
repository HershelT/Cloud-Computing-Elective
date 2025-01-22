from flask import Flask, request, jsonify
import requests
import os


app = Flask(__name__)

# Function to calculate the total gain for a list of stocks
def get_total_gain(stocks, stock_database_url):
    total_gain = 0
    # Loop through each stock and get the /stock-value from the appropriate data source
    for stock in stocks:
        # Get the stock value from the stock database
        response = requests.get(f"{stock_database_url}/stock-value/{stock['id']}")
        if response.status_code == 200: # If the response is valid, calculate the total gain
            total_gain += float(response.json()['stock value']) - (float(stock['purchase price']) * float(stock['shares']))
    return total_gain

# Route to calculate the capital gains which takes in query parameters (if any)
@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    filters = request.args.to_dict()
    stocks_url = 'http://stocks:8000/stocks'
    total_gains_stock1 = 0
    query_string = ''
    valid_query = True
    valid_queries = ['numsharesgt', 'numshareslt', 'id']
    if '?' in request.url:
        if not all(key in valid_queries for key in filters.keys()):
            valid_query = False
        # filter by number of shares and append to url
        if 'numsharesgt' in filters:
            gt = filters['numsharesgt']
            if gt.isdigit():
                query_string += '&numsharesgt=' + gt
            else:
                valid_query = False
        if 'numshareslt' in filters:
            lt = filters['numshareslt']
            if lt.isdigit():
                query_string += '&numshareslt=' + lt
            else:
                valid_query = False
        # filter by stock id and append to url
        if 'id' in filters:
            id = str(filters['id'])
            query_string += '&id=' + id
            
    if not valid_query:
        return jsonify({'error': f'Invalid query {filters}'}), 400
    
    response = requests.get(stocks_url + '?' + query_string)
    if response.status_code == 200:
        stocks = response.json()
        total_gains_stock1 = get_total_gain(stocks, 'http://stocks:8000')
    return jsonify({'total gains': total_gains_stock1}), 200

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting capital-gains service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

