import pytest
import requests


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
# Store all stocks [0, 1, 2, 3]
# ALL_STOCKS = [google_stock, apple_stock, nvidia_stock, tesla_stock]

# URL of kubernetics cluster, access everything throughb nginx
LOCAL_URL = 'http://127.0.0.1:80/'

# Post stocks to the stocks service
def post_stock(stock):
    # Post stocks to the stocks service
    response = requests.post(LOCAL_URL + 'stocks', json=stock)
    # Return response and status code
    return [response.json(), response.status_code]

def put_stock(stock, id):
    # add "id" label to copy of stock
    deepcopy_stock = stock.copy()
    deepcopy_stock['id'] = id
    # Put the stock
    response = requests.put(LOCAL_URL + 'stocks/' + id, json=deepcopy_stock)
    return [response.json(), response.status_code]

def get_stocks():
    response = requests.get(LOCAL_URL + 'stocks')
    # assert response.status_code == 200
    return [response.json(), response.status_code]

# Delete all stocks that were posted
def delete_all():
    response = get_stocks()[0]
    for stock in response:
        id = stock['id']
        response = requests.delete(LOCAL_URL + 'stocks/' + id)
        assert response.status_code == 204
    


# post stock and get it
def test_get():
    # Delete all stocks
    delete_all()
    # Post Google Stock
    post_result = post_stock(google_stock)
    # Test if the stock was posted
    assert post_result[1] == 201
    # Get the id of the stock  
    id = post_result[0]['id']
    # Get all stocks
    get_result = get_stocks()
    # Check if the get request was successful
    assert get_result[1] == 200
    # Get all stocks
    all_stocks = get_result[0]
    # Check if the stock is in the list
    for stock in all_stocks:
        if stock['id'] == id:
            assert stock["symbol"] == google_stock["symbol"]
    # Attempt to post same stock symbol again
    post_status = post_stock(google_stock)
    assert post_status[1] == 400

def test_two():
    # Replace the google stock with tesla
    id = get_stocks()[0][0]['id']
    put_status = put_stock(tesla_stock, id)
    # print this log
    print()
    assert put_status[1] == 200
    # Ensure id is the same
    assert put_status[0]['id'] == id
    # Get Stocks and ensure the new symbol is tesla symbol
    for stock in get_stocks()[0]:
        if stock['id'] == 3:
            assert stock['symbol'] == tesla_stock['symbol']
    # Attempt to put stock with invalid id
    put_status = put_stock(tesla_stock, '123')
    assert put_status[1] == 404

# Run test_one
if __name__ == "__main__":
    print("Running tests")
    pytest.main()

