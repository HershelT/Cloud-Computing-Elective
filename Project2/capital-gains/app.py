from flask import Flask, request, jsonify
import requests

app = Flask(__name__)


def get_total_gain(stocks, stock_database_url):
    total_gain = 0
    # Loop through each stock and get the /stock-value from the appropriate data source
    for stock in stocks:
        response = requests.get(f"{stock_database_url}/stock-value/{stock['_id']}")
        if response.status_code == 200:
            total_gain += response.json()['stock value'] - stock['purchase price'] * stock['shares']
    return total_gain


@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    filters = request.args.to_dict()
    stocks1_url = 'http://stocks1-a:8000'
    stocks2_url = 'http://stocks2:8000'
    get_stock1 = True
    get_stock2 = True
    total_gains_stock1 = 0
    total_gains_stock2 = 0
    # check if portfolio is stock1 or stock2
    if 'portfolio' in filters:
        if filters['portfolio'] == 'stock1':
            get_stock2 = False
        elif filters['portfolio'] == 'stock2':
            get_stock1 = False
    # filter by number of shares and append to url
    if get_stock1:
        if 'numsharesgt' in filters:
            stocks1_url += '&numsharesgt=' + filters['numsharesgt']
        if 'numshareslt' in filters:
            stocks1_url += '&numshareslt=' + filters['numshareslt']
    elif get_stock2:
        if 'numsharesgt' in filters:
            stocks2_url += '&numsharesgt=' + filters['numsharesgt']
        if 'numshareslt' in filters:
            stocks2_url += '&numshareslt=' + filters['numshareslt']
    
    # get stocks from the appropriate data source
    # Then call get_total_gain to calculate the total gains
    if get_stock1 and get_stock2:
        response1 = requests.get(stocks1_url + '/stocks')
        response2 = requests.get(stocks2_url + '/stocks')
        total_gains_stock1 = get_total_gain(response1.json(), stocks1_url)
        total_gains_stock2 = get_total_gain(response2.json(), stocks2_url)
    elif get_stock1:
        response1 = requests.get(stocks1_url).json()
        total_gains_stock1 = get_total_gain(response1, stocks1_url)
    else:
        response2 = requests.get(stocks2_url).json()
        total_gains_stock2 = get_total_gain(response2, stocks2_url)
    
    total_gains = total_gains_stock1 + total_gains_stock2
    return jsonify({"capital gains": total_gains}), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)