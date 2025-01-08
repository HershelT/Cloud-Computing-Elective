
## PROJECT 2

A simple project that demonstrates the use of Docker and Docker Compose to run multiple services. The project consists of three services: NGINX, Stocks1, Stocks2, and Capital-Gains. The NGINX server routes requests to the Stocks1 and Stocks2 servers. The Stocks1 and Stocks2 servers return a list of stocks, a specific stock, the value of a specific stock, and the total value of all stocks in the portfolio at the current time. The Capital-Gains server returns the capital gains of both stocks1 and stocks2 at the current time.

All of these use a persistent MongoDB database to store the stock information. Even if the servers are killed, the data will still be available when the servers are restarted.


Run `docker-compose up --build` to build and run the project. 

The project will be running on multiple ports as specified in the `docker-compose.yml` file.

## How to run the tests
To test the project you can use Postman or any other API testing tool.

# NGINX

The NGINX server is running on port 80 and only accepts Get requests for the `/stocks1` and `/stocks2` endpoints.
The NGINX will then route the requests to the respective stocks1 and stocks2 servers using the container port 8000.

Website can be accessed at `http:/localhost`

Functions of the NGINX server:

`/stocks1` endpoint that routes to the stocks1 server.

`/stocks2` endpoint that routes to the stocks2 server.

`/stocks1/<id>` endpoint that routes to the stocks1 server.

`/stocks2/<id>` endpoint that routes to the stocks2 server.

# Stocks1 and Stocks2

The stocks1 server is running on host port 5001 and the stocks2 server is running on host port 5002.
Can both be called by running `http://localhost:5001/stocks1` and `http://localhost:5002/stocks2` respectively.

Functions in the stocks1 and stocks2 servers are similar.

`/stocks` endpoint that returns a list of stocks.

`/stocks/<id>` endpoint that returns a specific stock.

`/stock-value/<id>` endpoint that returns the value of a specific stock.

`/portfolio-value` endpoint that returns the total value of all stocks in the portfolio at the current time.

`/kill` endpoint that kills the server, which automatically restarts due to the `restart: always` in the `docker-compose.yml` file.

# Capital-Gains

The capital-gains server is running on host port 5003.

Can be called by running `http://localhost:5003/capital-gains`.

Functions in the capital-gains server:

`/capital-gains` endpoint that returns the capital gains of both stocks1 and stocks2 at the current time.

Query parameters: (Can combine them using `&`)

`?portfolio=<stocks>` - The portfolio to calculate the capital gains for. The portfolio can be either `stocks1` or `stocks2`.

`?numshareslt=<num>` - The number of shares to filter by. Only stocks with less than the specified number of shares will be included in the calculation.

`?numsharesgt=<num>` - The number of shares to filter by. Only stocks with more than the specified number of shares will be included in the calculation.
