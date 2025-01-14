from flask import Flask, jsonify, request
from pymongo import MongoClient
import requests
from bson import ObjectId
from datetime import datetime

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

# Initialize MongoDB client
mongo_client = MongoClient('mongodb://mongodb:27017/')  # Assumes 'mongodb' as the service name
db = mongo_client['stock_data'] #Use the stock_data database
collection_name = os.environ.get('COLLECTION_NAME') # only allowed to be 'stocks1'.
collection = db[collection_name] #Create or use an existing collection

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
            return jsonify({"error" : "Malformed data"}), 400
        #Check if the stock name is already provided
        name = stock_data.get('name', "NA")
        #Check if purchase date is provided
        purchase_date = stock_data.get('purchase date', "NA")
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
        response_data = {"id" : str(stock_id)}
        return jsonify(response_data), 201
    except Exception as e:
        print("Exception: ", str(e))
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
    print("Updating stock with id: ", ObjectId(stock_id))
    # Log in console the request
    REQUESTS.inc()
    # Log that we are updating a stock
    app.logger.info(f"Updating stock with id: {stock_id}")
    try:
        content_type = request.headers.get('Content-Type')
        if content_type != 'application/json':
            return jsonify({"error" : "Expected application/json media type"}), 415
        stock_data = request.get_json()
        #check if ALL fields are provided
        required_fields = ['name', 'symbol', 'purchase price', 'purchase date', 'shares']
        if not all(field in stock_data for field in required_fields):
            return jsonify({"error:" : "Malformed data"}), 400
        # If 'id' or '_id' is not provided, return error
        if 'id' not in stock_data and '_id' not in stock_data:
            return jsonify({"error:" : "Malformed data"}), 400
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
            return jsonify({"error" : "Not found"}), 404
    except Exception as e:
        print("Exception: ", str(e))
        return jsonify({"server error" : str(e)}), 500
    return jsonify({"id" : str(stock_id)}), 200

