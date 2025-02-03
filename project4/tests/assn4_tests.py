import pytest
import requests

# Get stocks_list from root directory
from stocks_list import *
# Define stocks to perform operations on
# URL of docker container for stocks and capital-gains
STOCKS_URL = 'http://localhost:5001/'
CAPITAL_GAINS_URL = 'http://localhost:5003/'

# Post stocks to the stocks service
def post_stock(stock):
    # Post stocks to the stocks service
    response = requests.post(STOCKS_URL + 'stocks', json=stock)
    # Return response and status code
    return [response.json(), response.status_code]

# Update a specific stock
def put_stock(stock, id):
    # add "id" label to copy of stock
    deepcopy_stock = stock.copy()
    deepcopy_stock['id'] = id
    # Put the stock
    response = requests.put(STOCKS_URL + 'stocks/' + id, json=deepcopy_stock)
    return [response.json(), response.status_code]

# get specific stock
def get_stock(id):
    response = requests.get(STOCKS_URL + 'stocks/' + id)
    return [response.json(), response.status_code]

# get all stocks
def get_stocks():
    response = requests.get(STOCKS_URL + 'stocks')
    # assert response.status_code == 200
    return [response.json(), response.status_code]

# Get stock-value of specific stock
def get_stock_value(id):
    response = requests.get(STOCKS_URL + 'stock-value/' + id)
    return [response.json(), response.status_code]

# Delete specific stock
def delete_stock(id):
    response = requests.delete(STOCKS_URL + 'stocks/' + id)
    return response.status_code

# Delete all stocks that were posted
def delete_all():
    response = get_stocks()[0]
    for stock in response:
        id = stock['id']
        response = requests.delete(STOCKS_URL + 'stocks/' + id)
        assert response.status_code == 204

# Get all ids of stocks
def get_all_ids():
    response = get_stocks()
    all_stocks = response[0]
    global_id = [stock['id'] for stock in all_stocks]
    return global_id

# Ficture to store global_id
@pytest.fixture(scope='module')
def global_id():
    global_id = []
    yield global_id
# Ficture to store stock values
@pytest.fixture(scope='module')
def stock_value():
    stock_value = []
    yield stock_value

def test_1(global_id):
    # Execute three post requests on stock1-3
    stock1_result = post_stock(stock1)
    stock2_result = post_stock(stock2)
    stock3_result = post_stock(stock3)
    # Check if the status code is 201 for all
    assert stock1_result[1] == 201
    assert stock2_result[1] == 201
    assert stock3_result[1] == 201
    # assert all three have unique ids
    assert stock1_result[0]['id'] != stock2_result[0]['id']
    assert stock1_result[0]['id'] != stock3_result[0]['id']
    assert stock2_result[0]['id'] != stock3_result[0]['id']
    # add all three ids to a global list
    global_id.extend([stock1_result[0]['id'], stock2_result[0]['id'], stock3_result[0]['id']])

def test_2(global_id):
    # Execute a get stocks/id request for stock1
    stock1_get = get_stock(global_id[0])
    # Check if the status code is 200
    assert stock1_get[1] == 200
    # Check if the stock symbol is NVDA
    assert stock1_get[0]['symbol'] == 'NVDA'

def test_3():
    # Execute a get stocks request
    all_stocks = get_stocks()
    # Check if the status code is 200
    assert all_stocks[1] == 200
    # Check if the length of the list is 3
    assert len(all_stocks[0]) == 3

def test_4(global_id, stock_value):
    symbol_fields = ['NVDA', 'AAPL', 'GOOG']
    # execute 3 stock get requests for the three ids of stock1-3
    for id in global_id:
        stock = get_stock_value(id)
        # Check if the status code is 200
        assert stock[1] == 200
        # Check if the symbol equals its corresponding symbol in symbol_fields
        assert stock[0]['symbol'] == symbol_fields[global_id.index(id)]
        # Store all three stock values in a list
        stock_value.append(stock[0]['stock value'])

def test_5(stock_value):
    # Execute a get portfolio value request
    portfolio_value = requests.get(STOCKS_URL + 'portfolio-value')
    # Check if the status code is 200
    assert portfolio_value.status_code == 200
    # Assert that portfolio value is within bounds
    total_value = sum(stock_value)
    assert portfolio_value.json()['portfolio value']*0.97 <= total_value 
    assert portfolio_value.json()['portfolio value']*1.03 >= total_value

def test_6():
    # Execute a post request with stock 7
    stock7_result = post_stock(stock7)
    # Is succesful if status code is 400 (symbol not provided)
    assert stock7_result[1] == 400

def test_7(global_id):
    # Delete stock2 
    del_status = delete_stock(global_id[1])
    # Check if the status code is 204
    assert del_status == 204

def test_8(global_id):
    # Execute a get request for stock2
    stock2_get = get_stock(global_id[1])
    # Check if the status code is 404
    assert stock2_get[1] == 404

def test_9():
    # Execute a post request with stock 8
    stock8_result = post_stock(stock8)
    # Is succesful if status code is 400 (purchase date format)
    assert stock8_result[1] == 400


# Run all tests
if __name__ == "__main__":
    print("Running tests")
    pytest.main()


