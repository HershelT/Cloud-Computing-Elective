#!/bin/bash
# Delete old cluster if it exists
kind delete cluster --name kind
# Create a KIND cluster
kind create cluster --config kind-config.yaml
# Create a namespace
kubectl apply -f namespace.yaml
# Build docker images for capital-gains
cd capital-gains
docker build -t capital-gains -f Dockerfile .
kind load docker-image capital-gains 
kubectl apply -f .
# Go back to root directory
cd ..
# Build docker images for stocks
cd stocks
docker build -t stocks -f Dockerfile .
kind load docker-image stocks
kubectl apply -f .
# Deploy resources in Cluster
cd ..
cd nginx
kubectl apply -f .
cd ..
cd database
kubectl apply -f .
# Validate the deployment
kubectl get all -n multi-service-app