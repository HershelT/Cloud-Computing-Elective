from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

# Function to calculate the total gain for a list of stocks
def get_total_gain(stocks, stock_database_url):
    total_gain = 0
    # Loop through each stock and get the /stock-value from the appropriate data source
    for stock in stocks:
        # Get the stock value from the stock database
        response = requests.get(f"{stock_database_url}/stock-value/{stock['id']}")
        if response.status_code == 200:
            # If the response is valid, calculate the total gain
            total_gain += float(response.json()['stock value']) - (float(stock['purchase price']) * float(stock['shares']))
    return total_gain

# Route to calculate the capital gains which takes in query parameters (if any)
@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    # Get the query parameters
    filters = request.args.to_dict()
    stocks1_url = 'http://stocks1-a:8000/stocks'
    stocks2_url = 'http://stocks2:8000/stocks'
    #flags to check if we need to get stocks from stock1 or stock2
    get_stock1 = True
    get_stock2 = True
    total_gains_stock1 = 0
    total_gains_stock2 = 0
    query_string = '?'
    # check if portfolio is stock1 or stock2
    valid_query = True
    valid_queries = ['portfolio', 'numsharesgt', 'numshareslt']
    if '?' in request.url:
      if not all(key in valid_queries for key in filters.keys()):
        valid_query = False
      # filter by portfolio
      if 'portfolio' in filters:
        if filters['portfolio'] == 'stocks1':
          get_stock2 = False
        elif filters['portfolio'] == 'stocks2':
          get_stock1 = False
        else:
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
    
    # if query is invalid, return error
    if not valid_query:
      return jsonify({"error": f"Invalid query {filters}"}), 400
    
    #See if we need to get stocks from stock1 or stock2
    if get_stock1:
      stocks1_url += query_string
    elif get_stock2:
      stocks2_url += query_string
    
    # get stocks from the appropriate data source
    # Then call get_total_gain to calculate the total gains
    if get_stock1 and get_stock2:
        response1 = requests.get(stocks1_url)
        response2 = requests.get(stocks2_url)
        total_gains_stock1 = get_total_gain(response1.json(), 'http://stocks1-a:8000')
        total_gains_stock2 = get_total_gain(response2.json(), 'http://stocks2:8000')
    elif get_stock1:
        response1 = requests.get(stocks1_url).json()
        total_gains_stock1 = get_total_gain(response1, 'http://stocks1-a:8000')
    else:
        response2 = requests.get(stocks2_url).json()
        total_gains_stock2 = get_total_gain(response2, 'http://stocks2:8000')
    # Calculate the total gains from both
    total_gains = total_gains_stock1 + total_gains_stock2
    return jsonify({"capital gains": total_gains}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)