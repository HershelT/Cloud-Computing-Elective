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

ALL_STOCKS = [google_stock, apple_stock, nvidia_stock, tesla_stock]

# URL of kubernetics cluster, access everything throughb nginx
LOCAL_URL = 'http://127.0.0.1:80/'





# Post stocks to the stocks service
def post_stock(id):
    # Post stocks to the stocks service
    response = requests.post(LOCAL_URL + 'stocks', json=google_stock)
    # assert response.status_code == 201
    # Return id created from "id" : <id> and status code
    return [response.json()['id'], response.status_code]

def get_stocks():
    response = requests.get(LOCAL_URL + 'stocks')
    # assert response.status_code == 200
    return [response.json(), response.status_code]

# Delete all stocks that were posted
def delete_all():
    response = get_stocks()
    for stock in response:
        id = stock['id']
        response = requests.delete(LOCAL_URL + 'stocks/' + id)
        assert response.status_code == 204
    


# post stock and get it
def test_one():
    # Delete all stocks
    delete_all()
    # Post Google Stock
    post_result = post_stock(0)
    # Test if the stock was posted
    assert post_result[1] == 201
    # Get the id of the stock  
    id = post_result[0]
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
            return True
    # Attempt to post same stock again
    status = post_stock(0)
    if status == 400:
        return True



# Run test_one
if __name__ == "__main__":
    print("Running test one")
    pytest.main(['-k', 'test_one'])


