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

# Wait for all to be running:
sleep 10

# wait until all the Pods are in the Running state
timeout=300
interval=5 # Check every 5 seconds.
elapsed=0

function check_pods_running() {
  # Get the count of pods that are NOT in the 'Running' state.
  not_running_count=$(kubectl get pods --all-namespaces -o yaml |
     yq '.items[] | select(.status.phase != "Running" and .status.phase != "Succeeded") | length' | wc -l)

  echo "Pods not in 'Running' state: $not_running_count"

  if [ "$not_running_count" -eq 0 ]; then
    return 0 # All pods are running.
  else
    return 1 # There are pods not in the 'Running' state.
  fi
}

all_pods_running=false
while [ "$elapsed" -lt "$timeout" ]; do
  if check_pods_running; then
    echo "All pods are in the 'Running' state."
    all_pods_running=true
    break
  fi
  echo "Waiting for all pods to be in the 'Running' state..."
  sleep "$interval"
  elapsed=$((elapsed + interval))
done

if [ "$all_pods_running" = false ]; then
  echo "Timed out waiting for all pods to be in the 'Running' state."
  exit 1
fi

# Validate the deployment
kubectl get all -n multi-service-app

