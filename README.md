## MOST RECENT (or Important) Project HERE
# Multi-Service Application (Project 3)

This project demonstrates the deployment of a multi-service application using Kubernetes. The application consists of several microservices, including Stocks, Capital-Gains, MongoDB, and NGINX, orchestrated using Kubernetes.

Based off of Reichman Computer Science University Kubernetes assignment found at:
[yanivNaor92/cloud-computing](https://github.com/yanivNaor92/cloud-computing-k8s-assignment)

## Table of Contents

- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Setup](#setup)
- [Deploying the Application](#deploying-the-application)
- [Testing the Application](#testing-the-application)
- [Cleaning Up](#cleaning-up)
- [Directory Structure](#directory-structure)
- [Accessing the Application](#accessing-the-application)

## Architecture

The application consists of the following services:

1. **Stocks Service**: Manages stock data and provides RESTful APIs to create, read, update, and delete stock entries.
2. **Capital-Gains Service**: Calculates the capital gains for stocks managed by the Stocks service.
3. **MongoDB**: A NoSQL database used to persistently store stock data.
4. **NGINX**: Acts as a reverse proxy server, routing incoming HTTP requests to the appropriate backend services.
5. The following diagram shows a high-level architecture of the system you need to implement.  
![Architecture Diagram](Project3/architecture.png)

## Prerequisites

Before continuing, ensure you have the following tools installed on your computer:

- [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git)
- [Docker](https://docs.docker.com/engine/install/)
- [kind](https://kind.sigs.k8s.io/docs/user/quick-start/)
- [kubectl](https://kubernetes.io/docs/tasks/tools/)

## Setup

1. **Clone the Repository**:
   ```sh
   git clone https://github.com/HershelT/Cloud-Computing-Elective/tree/main/Project3
   ```
## Deploying the Application

1. **Deploy everything**:
   Make sure docker engine is running and execute the following command in bash:
   ```sh
   ./deploy.sh
   ```
   This will run all the deployments necessary, including assigning a namespace, etc.

## Testing the Application

1. **Testing using PyTest**:
   To test the application, run the following command:
   ```sh
   pytest -v multi-service-app/tests/assn3_tests.py
   ```

## Cleaning Up

1. **Delete the Kubernetes Cluster**:
   To delete the Kubernetes cluster, run the following command:
   ```sh
   kind delete cluster --name kind
   ```

## Directory Structure

The project directory structure is as follows:

```
├── kind-config.yaml
├── deploy.sh
├── test_stocks.py
├── README.md
├── architecture.png
|── test-submission.sh
├── multi-service-app/
│   ├── namespace.yaml
│   ├── stocks/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── app.py
│   │   └── Dockerfile
│   ├── capital-gains/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   └── app.py
│   │   └── Dockerfile
│   ├── database/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── persistentVolume.yaml
│   │   ├── persistentVolumeClaim.yaml
│   ├── nginx/
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── configmap.yaml
│   ├── tests/
│   │   ├── assn3_tests.py
│   │   ├── stocks_list.py

```

## ACCESSING THE APPLICATION

1. **Accessing All Services Through NGINX**:

   To access the Stocks service, open a web browser and navigate to `http://127.0.0.1:80/`.

   Check out the nginx/configmap.yaml file to see how the NGINX server is configured to route incoming requests to the appropriate backend services. (example: /stocks, /capital-gains, etc.)


## License

This project is licensed under the MIT License - All Asignments are given in the Reichman University Cloud Computing and Software Engineering Class