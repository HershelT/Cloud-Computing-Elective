from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

def get_total_gain(stocks):
    total_gain = 0
    for stock in stocks:
        current_value = float(stock['stock value'])
        purchase_price = float(stock['purchase price'])
        gain = current_value - purchase_price
        total_gain += gain
    return total_gain



@app.route('/capital-gains', methods=['GET'])
def capital_gains():
    filters = request.args.to_dict()
    stocks1_url = 'http://stocks1-a:8000/stocks'
    stocks2_url = 'http://stocks2:8000/stocks'
    get_stock1 = True
    get_stock2 = True
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
    
    if get_stock1 and get_stock2:
        response1 = requests.get(stocks1_url)
        response2 = requests.get(stocks2_url)
        response_all = response1.json() + response2.json()
    elif get_stock1:
        response_all = requests.get(stocks1_url).json()
    else:
        response_all = requests.get(stocks2_url).json()
    
    return jsonify({"capital gains": get_total_gain(response_all)}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)