# Project 4: Stock Portfolio Management with CI/CD

## Overview

This project is a stock portfolio management system that allows users to manage their stock investments. It includes functionalities to add, update, delete, and retrieve stock information, as well as calculate stock values and portfolio gains. The project is built using Flask for the backend and MongoDB for data storage. The system is containerized using Docker and orchestrated using Docker Compose.

## Features

- **Stock Management**: Add, update, delete, and retrieve stock information.
- **Stock Value Calculation**: Calculate the current value of stocks using an external API.
- **Portfolio Value Calculation**: Calculate the total value of the stock portfolio.
- **Capital Gains Calculation**: Calculate the capital gains for the portfolio.
- **Health Check**: Endpoint to check the health of the service.

## CI/CD Workflow

The project incorporates a CI/CD pipeline using GitHub Actions. The workflow is defined in the `.github/workflows/assignment4.yml` file and includes the following jobs:

### 1. Build Job

- **Checkout Code**: Checks out the project code from the repository.
- **Build Docker Images**: Builds Docker images for the `stocks` and `capital-gains` services.
- **Save Artifacts**: Saves the built Docker images as artifacts for use in subsequent jobs.
- **Log Information**: Logs the build status and other relevant information.

### 2. Test Job

- **Download Artifacts**: Downloads the Docker images built in the previous job.
- **Load Docker Images**: Loads the Docker images into the Docker daemon.
- **Run Docker Compose**: Starts the services using Docker Compose.
- **Run Tests**: Executes the test suite using `pytest` to verify the functionality of the services.
- **Log Test Results**: Logs the test results and uploads them as artifacts.

### 3. Query Job

- **Download Artifacts**: Downloads the Docker images built in the build job.
- **Load Docker Images**: Loads the Docker images into the Docker daemon.
- **Run Docker Compose**: Starts the services using Docker Compose.
- **Run Queries**: Executes specific queries against the running services and records the results.
- **Log Query Results**: Logs the query results and uploads them as artifacts.

## How to Run

### Prerequisites

- Docker
- Docker Compose
- Python 3.8+
- MongoDB

### Running Locally

1. **Clone the Repository**:
    ```bash
    git clone <repository-url>
    cd project4
    ```

2. **Set Up Environment Variables**:
    Create a `.env` file in the root directory with the following content:
    ```env
    API_KEY=<your_api_key>
    ```

3. **Build and Run Services**:
    ```bash
    docker-compose up --build
    ```

4. **Run Tests**:
    ```bash
    pytest tests/assn4_tests.py
    ```

### Running CI/CD Pipeline

The CI/CD pipeline is triggered automatically on a workflow dispatch event. You can also manually trigger the workflow from the GitHub Actions tab in your repository.

## Conclusion

This project demonstrates the integration of CI/CD practices using GitHub Actions to automate the build, test, and deployment processes. By following this approach, we ensure that the application is consistently built and tested, leading to higher code quality and faster delivery.