from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests
from datetime import datetime

from Project2.stocks2.APIKEY import KEY

import os

app = Flask(__name__)

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://mongodb:27017/')  # Assumes 'mongodb' as the service name
db = mongo_client['stock_data'] #Use the stock_data database
collection_name = os.getenv('COLLECTION_NAME','stocks2') # Can be 'stocks1' or 'stocks2'
collection = db[collection_name] #Create or use an existing collection

# POST /stocks
@app.route('/stocks', methods=['POST'])
def create_stock():
    print("Creating a new stock")
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error" : "Expected application/json media type"}), 415
        #Grab the stock from the request
        stock_data = request.json
        #check Required fields
        required_fields = ['purchase price', 'symbol', 'shares']
        if not all(field in stock_data for field in required_fields):
            return jsonify({"error:" : "Malformed data"}), 400
        #Check if the stock symbol is already provided
        if collection.find_one({'symbol': stock_data['symbol'].upper()}):
            print("POST request error: symbol already exists")
            return jsonify({"error" : "Malformed data"}), 400
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
            "name": name,
            "symbol": stock_data['symbol'].upper(),
            "purchase price": round(float(stock_data['purchase price']), 2),
            "purchase date": purchase_date,
            "shares": int(stock_data['shares']),
        }
        #Add stock to global dictionary
        result = collection.insert_one(stock)
        response_data = {"id" : str(result.inserted_id)}
        return jsonify(response_data), 201
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

# GET /stocks
@app.route('/stocks', methods=['GET'])
def get_stocks():
    print("Getting all stocks")
    try:
        stocks = list(collection.find())
        for stock in stocks:
             stock['_id'] = str(stock['_id'])
        return jsonify(stocks), 200
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

#GET /stocks/<id>
@app.route('/stocks/<stock_id>', methods=['GET'])
def get_stock(stock_id):
    print("Getting stock with id: ", stock_id)
    try:
        stock = collection.find_one({"_id":stock_id})
        if stock:
          stock['_id'] = str(stock['_id'])
          return jsonify(stock), 200
        else:
            print("GET request error: no such ID")
            return jsonify({"error" : "Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

#DELETE /stocks/<id>
@app.route('/stocks/<stock_id>', methods=['DELETE'])
def delete_stock(stock_id):
    print("Deleting stock with id: ", stock_id)
    try:
        result = collection.delete_one({"_id":stock_id})
        if result.deleted_count == 0:
            print("DELETE request error: no such ID")
            return jsonify({"error" : "Not found"}), 404
        return '', 204
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    
#PUT /stocks/<id>
@app.route('/stocks/<stock_id>', methods=['PUT'])
def update(stock_id):
    print("Updating stock with id: ", stock_id)
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error" : "Expected application/json media type"}), 415
        stock_data = request.get_json()
        #check if ALL fields are provided
        required_fields = ['name', 'symbol', 'purchase price', 'purchase date', 'shares']
        if not all(field in stock_data for field in required_fields):
            return jsonify({"error:" : "Malformed data"}), 400
        #Check if the stock exists
        result = collection.update_one({"_id":stock_id}, { "$set": {
            "name": stock_data['name'],
            "symbol": stock_data['symbol'].upper(),
            "purchase price": round(float(stock_data['purchase price']), 2),
            "purchase date": stock_data['purchase date'],
            "shares": int(stock_data['shares']),
        }})
        if result.matched_count == 0:
            print("PUT request error: no such ID")
            return jsonify({"error" : "Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify({"id" : stock_id}), 200

#GET stock-value/<id>
@app.route('/stock-value/<stock_id>', methods=['GET'])
def get_stock_value(stock_id):
    print("Getting stock value with id: ", stock_id)
    try:
        stock = collection.find_one({'_id': stock_id})
        if not stock:
            print("GET request error: no such ID")
            return jsonify({"error" : "Not found"}), 404
        #Get the stock symbol
        symbol = stock['symbol']
        #Get the stock purchase price
        api_url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(symbol)
        response = requests.get(api_url, headers={'X-Api-Key': KEY})
        #Check if the response is valid
        if not response.status_code == requests.codes.ok:
            print("GET request error: ", response.status_code)
            return jsonify({"server error" : "API response code " + str(response.status_code)}), 500
        #Get the current stock price from response
        current_price = response.json()['price']
        #Calculate the stock value times how many shares
        stock_value = round(float(current_price * stock['shares']), 2)
        #return a json with the stock value
    
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify({
            "symbol": symbol,
            "ticker": current_price,
            "stock value": stock_value
        }), 200

#GET /portfolio-value
@app.route('/portfolio-value', methods=['GET'])
def get_portfolio_value():
    print("Getting portfolio value")
    try:
        total_value = 0
        for stock in collection.find():
            #Get the stock symbol
            symbol = stock['symbol']
            #Get the stock purchase price
            api_url = 'https://api.api-ninjas.com/v1/stockprice?ticker={}'.format(symbol)
            response = requests.get(api_url, headers={'X-Api-Key': KEY})
            #Check if the response is valid
            if not response.status_code == requests.codes.ok:
                print("GET request error: ", response.status_code)
                return jsonify({"server error" : "API response code " + str(response.status_code)}), 500
            #Get the current stock price from response
            current_price = response.json()['price']
            #Calculate the stock value times how many shares
            stock_value = int(current_price) * int(stock['shares'])
            #Add the stock value to the total value
            total_value += stock_value
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify({
        # REturn date in Day mont year format (DD-MM-YYYY)
        "date" : datetime.now().strftime("%d-%m-%Y"),
        "portfolio value": round(float(total_value), 2)
    }), 200

@app.route('/kill', methods=['GET'])
def kill_container():
  os._exit(1)

#Starting the service
if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))
    print(f"Starting the Stock Portfolio Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)