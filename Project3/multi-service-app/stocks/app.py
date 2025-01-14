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



