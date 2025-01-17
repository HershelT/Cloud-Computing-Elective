# Cloud Computing K8s Home Assignment
A home assignment for the Cloud Computing course at Reichman University.

## Introduction
In this assignment, you will explore the fundamentals of Kubernetes as covered in the lecture.
This exercise is designed to give you hands-on experience with Kubernetes, guiding you through the essential concepts and practices that underlie this powerful orchestration tool.
You will create a Kubernetes cluster and learn how to define and deploy applications within it by creating key resources like Deployments and Services.
These components will allow you to understand how Kubernetes manages application availability, scalability, and networking within a cluster.

Through this assignment, you'll gain practical insights into the structure and function of Kubernetes resources, which are essential for running and maintaining distributed applications.
By the end, you should have a foundational grasp of how to set up and manage applications in Kubernetes, preparing you for more advanced topics and real-world applications in container orchestration.  

## Prerequisites

Before continuing to the tasks, ensure the following tools are installed on your computer:

* [Git](https://git-scm.com/book/en/v2/Getting-Started-Installing-Git).
* [Docker](https://docs.docker.com/engine/install/).
* [kind](https://kind.sigs.k8s.io/docs/user/quick-start/).
* [kubectl](https://kubernetes.io/docs/tasks/tools/).

## Clone the Git Repository
To access the files in this repository you should first clone it to your local computer.

```shell
git clone https://github.com/yanivNaor92/cloud-computing-k8s-assignment
cd cloud-computing-k8s-assignment
``` 
Note: Make sure to run the commands in the following tasks from the root directory of this repository (unless instructed otherwise).

## Task 1 - Create a Sample Kubernetes Application
The following steps will guide you through creating the local Kubernetes cluster and deploy a sample application in the cluster.

### Step 1.1 - Create a KIND cluster
To create a Kubernetes cluster using KIND, run the following command in your terminal (make sure your Docker engine is
running first):

```shell
kind create cluster --config kind-config.yaml
```

If the installation was successful, you should see an output similar to the following:

```shell
Creating cluster "kind" ...
 ✓ Ensuring node image (kindest/node:v1.30.0) 🖼
 ✓ Preparing nodes 📦
 ✓ Writing configuration 📜
 ✓ Starting control-plane 🕹️
 ✓ Installing CNI 🔌
 ✓ Installing StorageClass 💾
Set kubectl context to "kind-kind"
You can now use your cluster with:

kubectl cluster-info --context kind-kind

Have a nice day! 👋
```

To ensure your kubectl context is pointing to your kind cluster, run the following command:

```shell
kubectl cluster-info
```

The output should be similar to the following:

```shell
Kubernetes control plane is running at https://127.0.0.1:43581
CoreDNS is running at https://127.0.0.1:43581/api/v1/namespaces/kube-system/services/kube-dns:dns/proxy

To further debug and diagnose cluster problems, use 'kubectl cluster-info dump'.
```

### Step 1.2 - Create an Image of the Sample Application
Make sure you perfrom the commands in this step from the `sample-app` directory.  
In your terminal run the following command to navigate to the `sample-app` directory.
```shell
cd sample-app
```
Build the Docker image and load it to the cluster:
```shell 
docker build -t ecommerce-app:latest .
kind load docker-image ecommerce-app:latest 
```

### Step 1.3 - Deploy the Sample Application
1. Deploy the `Deployment` resource:
```shell
kubectl apply -f deployment.yaml
```
2. Verify the application Pod was created successfully:
```shell
kubectl get pods
```
### Step 1.4 - Expose Your Application to Network Traffic

1. Deploy the `Service` resource:
```shell
kubectl apply -f service.yaml
```

### Step 1.5 - Verify the Application is Up and Running
Open your browser at the following address: `http://localhost:8080`.  
You should see the application running.

### Step 1.6 - Scale out your application
Currently, your Deployment is configured to create only one instance of your application.  
You can create more replicas by running the following command:
```shell
kubectl scale deployment ecommerce-app --replicas=3
```
Note that the `replicas` field of the `Deployment` resource was changed from 1 to 3.
```shell
kubectl get deployment ecommerce-app -o yaml
```
Note that the cluster now have 3 Pod replicas of the ecommerce app:
```shell
kubectl get pods
```

The `Service` resource we created in step 1.4 will ensure the traffic is evenly distributed between all the Pod replicas.  
Execute the following command in your terminal:
```shell
curl http://localhost:8080/api/podName
```
The output should be the Pod's name that handled the request.  
Execute it a few more times and observe how the response changes between each call.  

## Task 2 - Deploying a Multi-Service Application with Kubernetes
In this assignment, you will build upon your previous experience with Docker Compose by deploying the same multi-service application using Kubernetes. You will implement the Kubernetes equivalent of the architecture described in Assignment #2, ensuring high availability, scalability, and robustness of the application.  

### Objectives
#### Deploy a Multi-Service Application
Use Kubernetes to deploy the following services:
* 2 instances of the stocks service from Assignment #1.
* 1 instance of the capital-gains service as described in Assignment #2.
* 1 database service (e.g., MongoDB or another DB of your choice).
* 1 reverse-proxy service using NGINX.

#### Service Resilience
Configure the stocks services for persistence, ensuring data is retained in the database after a crash or restart.

#### Load Balancing
Use Kubernetes Services to load balance traffic across the replicas of the stocks service.

#### Reverse Proxy Configuration
Configure NGINX as a reverse-proxy to route requests from outside of the cluster to the appropriate service.

### Architecture
The following diagram shows a high-level architecture of the system you need to implement.  
Note: Although it's not mentioned explicitly in the diagram, all of the micro-services (NGINX, stocks, capital-gains, database) in the system are exposed to network traffic by a Kubernetes `Service`. Only the stocks `Service` is mentioned in the diagram for simplification. 
![Architecture Diagram](architecture.png)

### Instructions
The following sections will guide you through the required steps to complete this task.  

#### Step 2.1 - Create a KIND cluster
Create the KIND cluster as you did in [step 1.1](#step-11---create-a-kind-cluster). You can use the same cluster from task 1 or create a new one.  
```shell
kind create cluster --config kind-config.yaml
```
#### Step 2.2 - Create a Namespace in the Cluster
All Kubernetes resources you implement in this task should be in the same namespace. This namespace should **not** be the `default` namespace.  
In Kubernetes, a namespace is also considered a resource and can be described by the following manifest:
```yaml
apiVersion: v1
kind: Namespace
metadata:
  name: <namespaces-name>
```  
You should create the manifest above, replace the `<namespaces-name>` with a name of your choice, and save it in a file named `namespace.yaml`.  
To create the namespace in the cluster, run the following command:
```shell
kubectl apply -f namespace.yaml
``` 
Make sure to use the same namespace in all the resources you create in the following steps.  

#### Step 2.2 - Implement the Micro Services
The files of each micro-service of the system should be placed in a dedicated folder. In the end, your entire solution should be organized in the following structure:  
```plaintext
cloud-computing-k8s-assignment/
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
```
Note: The above file structure assumes you implement the code in Python. If you use a different programming language, adjust the code file name accordingly.  
##### Stocks Service
This micro-service is the same stock service you implemented in assignments #1 and #2. It has to provide the same REST API and fulfill the same requirements as instructed in assignment #1.
Similar to assignment #1, you need to run **two** replicas of the stock service.  
**Unlike assignment #1**, both instances should listen to the same port. The user that calls the API of the stock service should not be aware of which instance handled the request. Each request should be load-balanced between the two instances.
You need to ensure the responses are consistent no matter which instance handled the request.
To implement this micro-service you need to create the following files:
* `deployment.yaml` - YAML specification of the `Deployment` Kubernetes resource that describes the stock Pods. 
* `service.yaml` - YAML specification of the `Service` Kubernetes resource that expose the stock pods to network traffic and load-balancing.
* `app.py` - The code implementation of the stocks container (assuming you use Python, adjust the file name if you use other programming languages). 
* `Dockerfile` - The Dockerfile used to build the stocks image.

Note: The stock service should use a NINJA API key. Ensure your API key is available for the service when the TA runs it (similar to assignment #1).  

##### Capital Gains Service
This micro-service is the same capital-gains service you implemented in assignment #2. It has to provide the same REST API and fulfill the same requirements as instructed in assignment #2.
You need to run **one** replica of this service.  
Unlike assignment #2, this service doesn't need to accept the `portfolio` query parameter. Instead, it will only communicate with the stock service, which loads balance the request to one of the instances. See [How to access a service in a Kubernetes](#how-to-access-a-service-in-a-kubernetes-cluster) for more details.  
To implement this micro-service you need to create the following files:
* `deployment.yaml` - YAML specification of the `Deployment` Kubernetes resource that describes the capital-gains Pod. 
* `service.yaml` - YAML specification of the `Service` Kubernetes resource that exposes the capital-gains pods to network traffic.
* `app.py` - The code implementation of the capital-service container (assuming you use Python, adjust the file name if you use other programming languages). 
* `Dockerfile` - The Dockerfile used to build the capital-gains image.

##### NGINX Service
This micro-service is used as a reverse proxy for accessing the stocks service. (as done in assignment #2). A user from outside of the cluster interacts with this service only. The NGINX proxy should forward each request to the relevant service according to the request's path (e.g. `/stocks`, `/capital-gains`, etc.).  
To implement this micro-service you need to create the following files:
* `deployment.yaml` - YAML specification of the `Deployment` Kubernetes resource that describes the nginx Pod. 
* `service.yaml` - YAML specification of the `Service` Kubernetes resource that exposes the nginx pod to **external** network traffic. Think which [Service type](https://kubernetes.io/docs/concepts/services-networking/service/#publishing-services-service-types) it needs to be. Hint: take a look at the `kind-config.yaml` file.    
* `configmap.yaml` - YAML specification of the `ConfigMap` Kubernetes resource that describes the nginx configurations.  
You can find more information about using `ConfigMap` in this [section](#config-maps).

##### DataBase Service
This micro-service is used to add persistency to the system.  
For each CRUD operation done by the stocks service, the data should be stored in the database. Remember that there are two instances of the stocks service that access the database and you cannot guarantee which instance handles the API request. Also, both instances may be handling requests simultaneously.  
Be aware that both instances write to the same database. You need to ensure they don't conflict with each other (for example, one instance tries to update a stock object when the other instance tries to delete the same object).  

To implement this micro-service you need to create the following files:
* `deployment.yaml` - YAML specification of the `Deployment` Kubernetes resource that describes the database Pod. 
* `service.yaml` - YAML specification of the `Service` Kubernetes resource that exposes the database pod to network traffic.  
* `persistentVolume.yaml` - YAML specification of the `PersistentVolume` Kubernetes resource.  
* `persistentVolumeClaim.yaml` - YAML specification of the `PersistentVolumeClaim` Kubernetes resource.  
You can find more information about `PersistentVolume` and `PersistentVolumeClaim` in this [section](#persistent-volumes).

#### Step 2.3 - Build the Docker Images and Load them Into the Cluster
After you create each service's code and Dockerfile, you should build their Docker images with the `docker build` command.  
```shell
docker build -t <image-name> -f <path-to-dockerfile> .
```
Note that the `image` field in the `Deployment` of each micro-service should match the image tag you specified when building the image.  
To avoid pushing the images to a public Docker registry such as [Docker Hub](https://hub.docker.com/), you should load the images into the cluster by running the following command:
```shell
kind load docker-image <image-name>
```
Note that for the NGINX and database (e.g. MongoDB) services, you can use a public Docker image instead of creating one yourself. You don't need to load public images into your KIND cluster manually.  
**Important**: To make K8s use the image you loaded instead of pulling it from outside of the cluster, you must specify the following field in the container template of the respective `Deployment` resource: `imagePullPolicy: IfNotPresent`.
See the example in the `sample-app/deployment.yaml` file.  

#### Step 2.4 - Deploy the Resources in the Cluster
You should use the `kubectl apply` command to deploy your resources into your cluster.  
1. Ensure you have your Kubernetes configuration file (e.g., `deployment.yaml`) ready.
2. Open your terminal.
3. Navigate to the directory containing your configuration file.
4. Ensure you are targeting your desired cluster.  
   This can be done by setting the `KUBECONFIG` environment variable to the path of the kube-config file.
   ```shell
   export KUBECONFIG="path/to/your/kubeconfig/file"
   ```
   or by placing the kube-config file in the default path: `~/.kube/config` (the `~` sign indicates the HOME directory).
5. Run the following command:
   ```shell
   kubectl apply -f deployment.yaml
   ```
   You should get a message indicating the resource was created. e.g. `deployment/ecommerce-app created`
6. Validate your resource was created as expected by running the following command:  
   ```shell
   kubectl get <resource-name> -n <resource-namespace> -o yaml 
   ``` 
After you deploy all the required resources of each microservice, proceed to the next step and test that the system is functioning as expected.  

#### Step 2.5 - Test the System Behavior
##### Verify your Components' Status 
First, you need to validate that all of your resources, especially your `Pods,` were created successfully.  
Run the following command to get all the Pods in a specific namespace (replace `<namespace>` with your namespace):
```shell
kubectl get pods -n <namespace>
``` 
The output should look as follows:
```shell
NAME                             READY   STATUS    RESTARTS   AGE
stocks-6d967d75cb-72xrw          1/1     Running   0          11h
stocks-6d967d75cb-ug84r          1/1     Running   0          11h
capital-gains-1d947a758b-g7bjj   1/1     Running   0          11h
nginx-5er68d65c9-tnsst           1/1     Running   0          11h
mongo-2q93yd1514-tbasyn          1/1     Running   0          11h
```
Note the `STATUS` column. If one of the `Pods` is not in the `Running` status, you should investigate what might cause it.  
You can view the Pod's definition and its `status` by running the following command:
```shell
kubectl get pods <pod-name> -n <namespace> -o yaml
```
The `status` section usually contains useful information about the Pod's health and the error description (if it exists).  
If the Pod's container prints any logs, you can view them by running the following command:
```shell
kubectl logs <pod-name> -n <namespace> -c <container-name>
```

##### Use the REST API
The REST API should be available for use at the address `http://127.0.0.1:80/`, which corresponds to the NGINX service.  
The NGINX should function as a reverse proxy and forward the request to the relevant service according to the request path. For example, a request to `http://127.0.0.1:80/stocks` should be forwarded to the `stocks` service.  
The services (stocks and capital-gains) should serve the same paths and HTTP methods as specified in assignments #1 and #2.  

##### Validate Data Persistency
As mentioned in the [DataBase Service](#database-service) section, the database service should store its data persistently on the host machine (the Node).  
To validate that, perform the following steps:
1. Invoke the `POST /stocks` API one or more times to save some data in the database.  
2. Invoke the `GET /stocks` API and view your stock data. You should get a list of the stocks you saved in the previous step.  
3. Run the following command to get the database's Pod name:
   ```shell
   kubectl get pods -n <namespace-name>
   ```
   You should see a list of all the pods, copy the name of your database Pod.
4. Delete the database Pod by running the following command:
   ```shell
   kubectl delete pod <pod-name> -n <namespace-name>
   ```
5. Ensure a new database Pod was created and it's in the `Running` status:
   ```shell
   kubectl get pods -n <namespace-name>
   ```
6. Invoke the `GET /stocks` API and view your stocks data. You should get the same list of stocks you got in step 2.  



### Submission
* Submit a zip file containing all code, Dockerfiles and YAML manifests as mentioned in [step 2.2](#step-22---implement-the-micro-services).
* Make sure your NINJA API key is included in the stocks service.  
* If submitting the work as a team, please attach a document listing the team members.

#### Test your Submission
To run a basic sanity test of your work before submitting it, you should run the shell script in this repository.  
The script ensures your files and folder structure are in the correct form as described in [step 2.2](#step-22---implement-the-micro-services).  
The script perform the following actions:
1. Creates a KIND cluster (the cluster is created with the name `test-submission`. Don't forget to delete it afterwards).  
2. Build the Docker images of the `stocks` and `capital-gains` deployments. The tag of those images is extracted from the respective `deployment.yaml` file.  
3. Deploy the K8s resources of each of the services into the created cluster.  
4. Wait for all the Pods to reach the `Running` state.  
5. Perform an HTTP request using the `curl` command to ensure the `stocks` and the `capital-gains` services are responsive.  

Before running the test script, ensure that the `multi-service-app` folder, containing your submission is in the same folder as the test script.  
Also, the `yq` command should be installed on your computer. You can download it from [here](https://github.com/mikefarah/yq/#install) (install v4.x of yq).  
To run the script run the following command from your terminal:
```shell
bash test-submission.sh
```
The script may accept two **optional** arguments:
```shell
bash test-submission.sh --timeout 300 --skip-create-cluster
```
* `timeout`:  the number of seconds to wait until all Pods become running (default is 300).  
* `skip-create-cluster`: skips the creation of the K8s cluster. This is useful if the script failed in the middle and you want to rerun it without creating the cluster again.  

If everything works as expected, the script should complete without any errors, and the following messages should appear:  
```text
The sanity test for http://localhost:80/stocks passed successfully.
The sanity test for http://localhost:80/capital-gains passed successfully.
```

## Clean up
To delete the kind cluster you created in this assignment run the following command:
```shell
kind delete cluster --name <cluster-name>
```
To get the list of KIND clusters and to ensure the cluster is deleted, run the following command:
```shell
kind get clusters
```

# Appendices
## How to Access a Service in a Kubernetes Cluster
When Pods within the same cluster need to communicate with each other, Kubernetes Services provide a stable endpoint.  
Assume a Service named `my-service` in the `default` namespace exposing port 80.  
A client can use the Service name (`my-service`) as the DNS hostname.  
Kubernetes’ internal DNS will resolve `my-service` to its cluster IP.  
Thus, a Pod in the same namespace as the Service can execute HTTP requests to the Service by using just its name. e.g. `curl http://my-service`.

However, if the Pod is in a different namespace than the Service, it must use its full name: `<service-name>.<namespace>.svc.cluster.local`.  
Assume a Service named `my-service` exists in the namespace `app-namespace`. A Pod in the `default` namespace can access the Service using: `curl http://my-service.app-namespace.svc.cluster.local`.  

## Config Maps
A `ConfigMap` in Kubernetes is an API object used to store non-confidential configuration data in key-value pairs. ConfigMaps decouple configuration artifacts from application code, enabling you to manage application settings separately from the container images.  
With `ConfigMap` we can configure applications with settings (e.g., environment variables, configuration files) and avoid hardcoding configuration in the application image.  
More information about `ConfigMap` can be found in Kubernetes [official documentation](https://kubernetes.io/docs/concepts/configuration/configmap/).  

### Mounting a ConfigMap into a Pod
ConfigMaps can be mounted into a Pod as a file or directory in the container.  
Assuming you have the following `ConfigMap`:
```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: app-config
  namespace: my-namespace
data:
  nginx.conf: |
    http {
      server {
        listen 80;
        location / {
          proxy_pass http://localhost:8080;
        }
      }
    }
```
Note the pipe sign `|`. It allows us to write a multi-line string in the `nginx.conf` field.
You can mount this `ConfigMap` to your `Pod` with `volumes` and `volumeMounts`:
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
  namespace: my-namespace
spec:
  containers:
  - name: app-container
    image: my-app-image
    volumeMounts:
    - name: config-volume
      mountPath: /etc/nginx/nginx.conf
      subPath: nginx.conf
  volumes:
  - name: config-volume
    configMap:
      name: app-config
```
Note that the `ConfigMap` and the `Pod` must be in the same namespace.  
 
## Persistent Volumes
In Kubernetes, a `PersistentVolume` (PV) is a storage resource provisioned in the cluster, while a `PersistentVolumeClaim` (PVC) is a request for storage by a Pod. Together, they enable Pods to store files persistently, even if the Pod is deleted or restarted.  
More information about persistent volumes can be found in Kubernetes [official documentation](https://kubernetes.io/docs/concepts/storage/persistent-volumes/).  

### Steps to Save Files Persistently on the Host Machine (Node)
1. Define the `PersistentVolume` (PV)  
The PV represents a piece of storage on the cluster. For saving files on the Node, use the `hostPath` volume type.
```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: host-pv
  namespace: my-namespace
spec:
  capacity:
    storage: 1Gi
  storageClassName: standard
  accessModes:
  - ReadWriteOnce
  hostPath:
    path: /mnt/data  # Path on the Node's filesystem
```
`hostPath`: Specifies the directory on the host Node where files will be stored.
`accessModes`: Controls how the volume can be accessed:
* `ReadWriteOnce`: Read/write by a single Pod.
* `ReadOnlyMany`: Read-only by multiple Pods.
* `ReadWriteMany`: Read/write by multiple Pods.

2. Define the PersistentVolumeClaim (PVC)  
A PVC is used by Pods to request storage from a PV.
```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: host-pvc
  namespace: my-namespace
spec:
  accessModes:
  - ReadWriteOnce
  storageClassName: standard
  resources:
    requests:
      storage: 500Mi
```
* The `accessModes` in the PVC must match the PV’s `accessModes`.
* The requested storage size (500Mi) must be less than or equal to the PV’s capacity.

3. Use the PVC in a Pod  
Mount the PVC as a volume in the Pod to persist files.
```yaml
apiVersion: v1
kind: Pod
metadata:
  name: app-pod
spec:
  containers:
  - name: app-container
    image: busybox
    command: ["sh", "-c", "echo 'Hello, World!' > /data/hello.txt && sleep 3600"]
    volumeMounts:
    - name: data-volume
      mountPath: /data
  volumes:
  - name: data-volume
    persistentVolumeClaim:
      claimName: host-pvc
```
* `volumeMounts`: Mounts the volume into the container’s filesystem at /data.
* `claimName`: Links the Pod to the PVC.
