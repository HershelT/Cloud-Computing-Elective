## PROJECT 2

A simple project that demonstrates the use of Docker and Docker Compose to run multiple services. The project consists of four services: NGINX, Stocks1, Stocks2, and Capital-Gains. The NGINX server routes requests to the Stocks1 and Stocks2 servers. The Stocks1 and Stocks2 servers provide RESTful APIs to manage stock data, including endpoints to create, read, update, and delete stock entries. The Capital-Gains server aggregates data from both Stocks1 and Stocks2 services to calculate the capital gains.

All of these use a persistent MongoDB database to store the stock information. Even if the servers are killed, the data will still be available when the servers are restarted.

### Key Components

1. **NGINX**: Acts as a reverse proxy server, routing incoming HTTP requests to the appropriate backend services (Stocks1 and Stocks2). It ensures that only GET requests are allowed for the `/stocks1` and `/stocks2` endpoints.

2. **Stocks1 and Stocks2**: These are two separate Flask-based microservices that manage stock data. Each service provides RESTful endpoints to:
   - **POST /stocks**: Create a new stock entry.
   - **GET /stocks**: Retrieve all stocks.
   - **GET /stocks/<id>**: Retrieve a specific stock by ID.
   - **PUT /stocks/<id>**: Update a stock by ID.
   - **DELETE /stocks/<id>**: Delete a stock by ID.
   - **GET /stock-value/<id>**: Calculate the current value of a specific stock.
   - **GET /portfolio-value**: Calculate the total value of all stocks in the portfolio.

3. **Capital-Gains**: A Flask-based microservice that calculates the capital gains for stocks managed by the Stocks1 and Stocks2 services. It aggregates data from both services and provides a comprehensive view of the capital gains.
   - **GET /capital-gains**: Calculate the capital gains for stocks managed by both Stocks1 and Stocks2 services.

4. **MongoDB**: A NoSQL database used to persistently store stock data. It ensures data durability and availability even if the services are restarted.

### How to Run

1. **Build and Run**: Use Docker Compose to build and run the application:
   ```sh
   docker-compose up --build