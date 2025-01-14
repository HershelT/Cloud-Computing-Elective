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


