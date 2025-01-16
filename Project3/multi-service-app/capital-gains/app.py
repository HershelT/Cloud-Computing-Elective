from flask import Flask, request, jsonify
import requests

# Added for kubernetics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil
import socket
import os


app = Flask(__name__)

# Prometheus metrics
REQUESTS = Counter('requests_total', 'Total requests')
LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')

# global variables for load simulation
request_count = 0
MEMORY_GROWTH_FACTOR = 5  # MB per request
memory_cache = []

# Get the hostname
hostname = socket.gethostname()



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
# We only have one service stocks1. We will use the same service to get the stocks.
# Thus, no portfolio filter is needed.
@app.route('/capital-gains', methods=['GET'])
@LATENCY.time()
def capital_gains():
    REQUESTS.inc()
    app.logger.info('Request received for /capital-gains')

    filters = request.args.to_dict()
    stocks1_url = ' http://stocks-service/stocks'
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
            # Check if its valid hash
            # if len(id) != 24:
            #     valid_query = False
            # else:
            query_string += '&id=' + id
            
    if not valid_query:
        return jsonify({'error': f'Invalid query {filters}'}), 400
    
    response = requests.get(stocks1_url + '?' + query_string)
    if response.status_code == 200:
        stocks = response.json()
        total_gains_stock1 = get_total_gain(stocks, ' http://stocks-service')
    return jsonify({'total gains': total_gains_stock1}), 200

if __name__ == '__main__':
    app.logger.setLevel('INFO')
    port = int(os.environ.get('PORT', 8080))
    print(f"Starting capital-gains service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)

