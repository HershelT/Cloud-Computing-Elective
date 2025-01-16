# Default values
timeout=300
skip_create_cluster=false
cluster_name=test-submission

# Parse arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        --timeout) timeout="$2"; shift ;;
        --skip-create-cluster) skip_create_cluster=true ;;
        *) echo "Unknown parameter passed: $1"; exit 1 ;;
    esac
    shift
done

if [ "$skip_create_cluster" = false ]; then
  echo "Creating a new KIND cluster"
  # check if KIND cluster already exists
  kind get clusters | grep -q $cluster_name
  if [ $? -eq 0 ]; then
    echo "kind cluster named $cluster_name already exists, please delete it before running this script"
    exit 1
  else
    echo "creating kind cluster"
    kind create cluster --name $cluster_name --config ./kind-config.yaml
  fi
fi

set -e

# Build the Docker images
stocks_image_name=$(yq eval '.spec.template.spec.containers[0].image' ./multi-service-app/stocks/deployment.yaml)
capital_gains_image_name=$(yq eval '.spec.template.spec.containers[0].image' ./multi-service-app/capital-gains/deployment.yaml)

if [[ "$stocks_image_name" = "null" || "$capital_gains_image_name" == "null" ]]; then
    echo "Error: failed to get the image name of the stocks or capital-gains services. Please check the deployment.yaml files."
    exit 1
fi

echo "building the stocks docker image with the following tag:" $stocks_image_name
docker build -t $stocks_image_name ./multi-service-app/stocks

echo "building the capital-gains docker image with the following tag:" $capital_gains_image_name
docker build -t $capital_gains_image_name ./multi-service-app/capital-gains

# Load the Docker images into the KIND cluster
kind load docker-image $stocks_image_name --name $cluster_name
kind load docker-image $capital_gains_image_name --name $cluster_name

# Create the namespace
kubectl apply -f ./multi-service-app/namespace.yaml

# Deploy nginx
kubectl apply -f ./multi-service-app/nginx/

# Deploy the stocks service
kubectl apply -f ./multi-service-app/stocks/

# Deploy the capital-gains service
kubectl apply -f ./multi-service-app/capital-gains/

# Deploy the database
kubectl apply -f ./multi-service-app/database/

sleep 10

# wait until all the Pods are in the Running state
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

# Check that the stocks and capital-gains services are working
urls=("http://localhost:80/stocks" "http://localhost:80/capital-gains")
for url in "${urls[@]}"; do
    http_status=$(curl -s -o /dev/null -w "%{http_code}" "$url")

    # Check the response status code is 200
    if [[ "$http_status" == "200" ]]; then
        echo "The sanity test for $url passed successfully."
    else
        echo "It seems that the following URL is not working as expected. Please verify it before submitting your assignment"
        echo "URL: $url"
        echo "HTTP Status: $http_status"
        exit 1
    fi
done
