from flask import Flask, jsonify, request, make_response
import json
import requests
from datetime import datetime

from APIKEY import KEY


app = Flask(__name__) #initialize the app
Stocks = {}

id = 0
def generate_id():
    global id
    id += 1
    return id

# POST /stocks
@app.route('/stocks', methods=['POST'])
def create_stock():
    print("Creating a new stock")
    try:
        global Stocks
        #Grab the stock from the request
        stock_data = request.json
        #check Required fields
        required_fields = ['purchase price', 'symbol', 'shares']
        if not all(field in stock_data for field in required_fields):
            return jsonify({"error:" : "Malformed data"}), 400
        new_id = generate_id()
        #Check if the stock name is already provided
        if 'name' not in stock_data:
            name = "NA"
        else:
            name = stock_data['name']
        #Check if purchase date is provided
        if 'purchase date' not in stock_data:
            purchase_date = "NA"
        else:
            purchase_date = stock_data['purchase date']
        stock = {
            "id": str(new_id),
            "name": name,
            "symbol": stock_data['symbol'].upper(),
            "purchase price": round(float(stock_data['purchase price']), 2),
            "purchase date": purchase_date,
            "shares": int(stock_data['shares']),
        }
        #Add stock to global dictionary
        Stocks[new_id] = stock
        response_data = {"id" : new_id}
        return jsonify(response_data), 201
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

# GET /stocks
@app.route('/stocks', methods=['GET'])
def get_stocks():
    print("Getting all stocks")
    try:
        return list(Stocks.values()), 200
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

#GET /stocks/<id>
@app.route('/stocks/<int:id>', methods=['GET'])
def get_stock(id):
    print("Getting stock with id: ", id)
    try:
        stock = Stocks[int(id)]
    except KeyError:
        print("GET request error: no such ID")
        return jsonify({"error" : "Stock not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify(stock), 200

#Use API to get current stock value



#GET stock-value/<id>
@app.route('/stock-value/<int:id>', methods=['GET'])
def get_stock_value(id):
    print("Getting stock value with id: ", id)
    try:
        stock = Stocks[int(id)]
        #Get the stock symbol
        symbol = stock['symbol']
        #Get the stock purchase price
        api_url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(symbol)
        response = requests.get(api_url, headers={'X-Api-Key': KEY})
        #Get the current stock price from response
        current_price = response.json()['price']
        #Calculate the stock value times how many shares
        stock_value = round(float(current_price * stock['shares']), 2)
        #return a json with the stock value
    except KeyError:
        print("GET request error: no such ID")
        return jsonify({"error" : "Stock not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify({
            "symbol": symbol,
            "ticker": current_price,
            "stock value": stock_value
        }), 200









#Starting the service
if __name__ == '__main__':
    print("Starting the Stock Portfolio Service")
    app.run(host='0.0.0.0', port=8001, debug=True)






