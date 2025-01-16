import pytest

# Define stocks to perform operations on
google_stock = {
    "name": "Google",
    "purchase date": "23-11-2012",
    "purchase price": 100.00,
    "shares": 35,
    "symbol": "GOOG"
}

apple_stock = {
    "name": "Apple",
    "purchase date": "5-1-2018",
    "purchase price": 75.55,
    "shares": 30,
    "symbol": "AAPL"
}

nvidia_stock = {
    "name": "Nvidia",
    "purchase date": "3-4-2019",
    "purchase price": 201.567,
    "shares": 20,
    "symbol": "NVDA"
}

tesla_stock = {
    "name": "Tesla",
    "purchase date": "7-8-2020",
    "purchase price": 124.50,
    "shares": 42,
    "symbol": "TSLA"
}

# URL of kubernetics cluster, access everything throughb nginx
LOCAL_URL = 'http://127.0.0.1:80/