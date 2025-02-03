import requests

from stocks_list import *

# URLS for the services
STOCKS_URL = 'http://localhost:5001/'
CAPITAL_GAINS_URL = 'http://localhost:5003/'

# Post the first 6 stocks
def post_stocks():
    stocks = [stock1, stock2, stock3, stock4, stock5, stock6]
    for stock in stocks:
        response = requests.post(STOCKS_URL + 'stocks', json=stock)
        assert response.status_code == 201

# Post the first 6 stocks
post_stocks()

query_lines = []
# Read each line of the query.txt file
with open('query.txt', 'r') as file:
    for line in file:
        query_lines.append(line)

# For each line perform
"""
if line is of form "stocks:<qs>", execute get /stocks with query string qs
if line is of form "capital-gains:<qs>", execute get /capital-gains with query string qs
"""
# check the <service-name>:<query-string> format
for line in query_lines:
    # If line is of form "stocks:<qs>"
    if "stocks:" in line:
        # Get the query string
        qs = line.split(":")[1].strip()
        # Get the response
        response = requests.get(STOCKS_URL + 'stocks?' + qs)
        # Print the response
        print(response.json())
        # Add qs: line to response.txt file
        with open('response.txt', 'a') as file:
            file.write(f"qs: {line.strip()}\n")
            file.write(f"json: \n{response.json()}\n")
    # If line is of form "capital-gains:<qs>"
    elif "capital-gains:" in line:
        # Get the query string
        qs = line.split(":")[1].strip()
        # Get the response
        response = requests.get(CAPITAL_GAINS_URL + 'capital-gains?' + qs)
        # Print the response
        print(response.json())
        # Add qs: line to response.txt file
        with open('response.txt', 'a') as file:
            file.write(f"qs: {line.strip()}\n")
            file.write(f"json: \n{response.json()}\n")

