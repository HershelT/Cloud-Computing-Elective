from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests
from bson import ObjectId
from datetime import datetime
import subprocess


# Added for kubernetics
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import psutil
import socket

from APIKEY import KEY

import os

app = Flask(__name__)


# Prometheus metrics
REQUESTS = Counter('requests_total', 'Total requests')
LATENCY = Histogram('request_latency_seconds', 'Request latency in seconds')

# Global variables for load simulation
request_count = 0
MEMORY_GROWTH_FACTOR = 5  # MB per request
memory_cache = []

# Initialize MongoDB client deployed in the same Kubernetes cluster
mongo_client = MongoClient('mongodb://mongodb.multi-service-app.svc.cluster.local:27017/')  # Assumes 'mongodb' as the service name
db = mongo_client['stock_data'] #Use the stock_data database
# collection_name = os.environ.get('COLLECTION_NAME') # only allowed to be 'stocks1'.
collection = db["stocks"] #Create or use an existing collection

# Get the hostname of the pod for testing purposes
hostname = socket.gethostname()

# POST /stocks
@app.route('/stocks', methods=['POST'])
@LATENCY.time()
def create_stock():
    print(f"Creating a new stock on {hostname}")
    # Log in console the request
    REQUESTS.inc()
    # Log that we are creating a new stock
    app.logger.info("Creating a new stock")
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
            app.logger.error(f"Error creating stock: symbol {stock_data['symbol']} already exists")
            return jsonify({"error" : "Malformed data"}), 400
        #Check if the stock name is already provided
        name = stock_data.get('name', "NA")
        #Check if purchase date is provided
        purchase_date = stock_data.get('purchase date', "NA")
        try:
            datetime.strptime(purchase_date, '%d-%m-%Y')
        except ValueError:
            print("POST request error: purchase date is not in DD-MM-YYYY format")
            app.logger.error(f"Error creating stock: purchase date {purchase_date} is not in DD-MM-YYYY format")
            return jsonify({"error" : "Malformed data"}), 400
        # Create a new stock object
        stock_id = str(ObjectId())
        stock = {
            "id": stock_id,
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
        app.logger.error(f"Error creating stock: {str(e)}")
        return jsonify({"server error" : str(e)}), 500

# GET /stocks
@app.route('/stocks', methods=['GET'])
@LATENCY.time()
def get_stocks():
    print("Getting all stocks")
    # Log in console the request
    REQUESTS.inc()
    # Log that we are getting all stocks
    app.logger.info("Getting all stocks")
    try:
      filters = request.args.to_dict()
      filtered_stocks = []
      for stock in collection.find():
        match = True
        # Check if the stock matches the filters from the query string
        if 'numsharesgt' in filters:
            match = match and float(stock['shares']) > float(filters['numsharesgt'])
        if 'numshareslt' in filters:
            match = match and float(stock['shares']) < float(filters['numshareslt'])
        # Add a query to check if stock id is in the filters
        if 'id' in filters:
            match = match and str(stock['_id']) == filters['id']
        if match:
          stock['id'] = str(stock.pop('_id'))
          filtered_stocks.append(stock)
      return jsonify(filtered_stocks), 200
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

# GET /stocks/<id>
@app.route('/stocks/<stock_id>', methods=['GET'])
@LATENCY.time()
def get_stock(stock_id):
    print("Getting stock with id: ", stock_id)
    # Log in console the request
    REQUESTS.inc()
    # Log that we are getting a stock
    app.logger.info(f"Getting stock with id: {stock_id}")
    # See if id is a valid ObjectId
    try:
        ObjectId(stock_id)
    except:
        return jsonify({"error" : "Not found"}), 404
    try:
        stock = collection.find_one({"_id": ObjectId(stock_id)})
        if stock:
          stock['_id'] = str(stock['_id'])
          stock['id'] = stock.pop('_id')
          return jsonify(stock), 200
        else:
            print("GET request error: no such ID")
            return jsonify({"error" : "Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500

# DELETE /stocks/<id>
@app.route('/stocks/<stock_id>', methods=['DELETE'])
@LATENCY.time()
def delete_stock(stock_id):
    print("Deleting stock with id: ", stock_id)
    # Log in console the request
    REQUESTS.inc()
    # Log that we are deleting a stock
    app.logger.info(f"Deleting stock with id: {stock_id}")
    # See if id is a valid ObjectId
    try:
        ObjectId(stock_id)
    except:
        return jsonify({"error" : "Not found"}), 404
    try:
        result = collection.delete_one({"_id": ObjectId(stock_id)})
        if result.deleted_count == 0:
            return jsonify({"error" : "Not found"}), 404
        return '', 204
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    
# PUT /stocks/<id>
@app.route('/stocks/<stock_id>', methods=['PUT'])
@LATENCY.time()
def update(stock_id):
    # Log in console the request
    REQUESTS.inc()
    # Log that we are updating a stock
    app.logger.info(f"Updating stock with id: {stock_id}")
    # See if id is a valid ObjectId
    try:
        ObjectId(stock_id)
    except:
        return jsonify({"error" : "Not found"}), 404
    print("Updating stock with id: ", ObjectId(stock_id))
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error" : "Expected application/json media type"}), 415
        stock_data = request.get_json()
        #check if ALL fields are provided
        required_fields = ['name', 'symbol', 'purchase price', 'purchase date', 'shares']
        if not all(field in stock_data for field in required_fields):
            app.logger.error("Error updating stock: Malformed data")
            return jsonify({"error:" : "Malformed data"}), 400
        # If 'id' or '_id' is not provided, return error
        if 'id' not in stock_data and '_id' not in stock_data:
            return jsonify({"error:" : "Malformed data"}), 400
        # Check if stock purchase dat is in MM-DD-YYYY format
        try:
            datetime.strptime(stock_data['purchase date'], '%d-%m-%Y')
        except ValueError:
            print("POST request error: purchase date is not in DD-MM-YYYY format")
            app.logger.error(f"Error creating stock: purchase date {stock_data['purchase date']} is not in DD-MM-YYYY format")
            return jsonify({"error" : "Malformed data"}), 400
        #Check if the stock exists
        result = collection.update_one({"_id":ObjectId(stock_id)}, { "$set": {
            "id": str(stock_id),
            "name": stock_data['name'],
            "symbol": stock_data['symbol'].upper(),
            "purchase price": round(float(stock_data['purchase price']), 2),
            "purchase date": stock_data['purchase date'],
            "shares": int(stock_data['shares']),
        }})
        if result.matched_count == 0:
            print("PUT request error: no such ID")
            app.logger.error(f"Error updating stock: no such ID {stock_id}")
            return jsonify({"error" : "Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify({"id" : str(stock_id)}), 200

#GET stock-value/<id>
@app.route('/stock-value/<stock_id>', methods=['GET'])
@LATENCY.time()
def get_stock_value(stock_id):
    print("Getting stock value with id: ", stock_id)
    # Log in console the request
    REQUESTS.inc()
    # Log that we are getting the stock value
    app.logger.info(f"Getting stock value with id: {stock_id}")
    # See if id is a valid ObjectId
    try:
        ObjectId(stock_id)
    except:
        return jsonify({"error" : "Not found"}), 404
    try:
        # Convert stock_id to ObjectId
        stock = collection.find_one({'_id': ObjectId(stock_id)})
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
@LATENCY.time()
def get_portfolio_value():
    print("Getting portfolio value")
    # Log in console the request
    REQUESTS.inc()
    # Log that we are getting the portfolio value
    app.logger.info("Getting portfolio value")
    try:
        total_value = 0
        for stock in list(collection.find()):
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

# #GET /kill
# @app.route('/kill', methods=['GET'])
# def kill_container():
#     # restart the database
#     # Find the id of mongo-deployment and fecth the response
#     response = os.popen('kubectl get pods -n multi-service-app | grep mongo-deployment').read()
#     response = response.split(' ')[0]
#     # Delete the pod
#     os.system(f'kubectl delete pod {response} -n multi-service-app')
#     return f'Killing the container{response}', 200

@app.route('/kill', methods=['GET'])
def kill_container():
    try:
        # Find the id of mongo-deployment pod
        response = subprocess.check_output(
            "kubectl get pods -n multi-service-app -o custom-columns=:metadata.name | grep mongo-deployment", shell=True
        ).decode('utf-8').strip()
        
        # Delete the pod
        subprocess.check_call(f'kubectl delete pod {response} -n multi-service-app', shell=True)
        
        return f'Killing the container {response}', 200
    except subprocess.CalledProcessError as e:
        return f'Error: {str(e)}', 500



#GET podName
@app.route('/podName', methods=['GET'])
@LATENCY.time()
def get_pod_name():
    return hostname, 200

#GET /healthz
@app.route('/healthz', methods=['GET'])
def healthz():
    return 'OK', 200

#GET /metrics
@app.route('/metrics', methods=['GET'])
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

# Starting the service
if __name__ == '__main__':
    # Add debug logging
    app.logger.setLevel('INFO')
    port = int(os.getenv('PORT', 8000))
    print(f"Starting the Stock Portfolio Service on port {port}")
    app.run(host='0.0.0.0', port=port, debug=True)
