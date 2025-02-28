# Running and Debugging PySpark Code on Kubernetes

This guide explains how to set up and run PySpark code on a Kubernetes cluster using an IDE. You will create a driver pod, configure IDE for remote development, and enable debugging.

## Prerequisites

- Kubernetes cluster with Spark installed

- kubectl configured to access the cluster

- Docker (for building and pushing images)

## 1. Setting Up Kubernetes Configuration
To directly access your Kubernetes cluster and run kubectl commands through your IDE, follow these steps:
1. Install kubectl. For Mac, it is downloaded as shown below. For other platforms, you can refer to the documentation online.
```bash
 brew install kubectl
```

2. Download KubeConfig (xxx.yaml) from 
   - Rancher or
   - AWS EKS
   - Google GKE
   - Minikube
   - Azure AKS ...
3. Configure Kubernetes cluster access:
```bash
cp /xxxxxx/xxx.yaml ~/.kube/config
```
4. To isolate your Spark resources, create a spark namespace in Kubernetes:
```bash
kubectl create namespace spark
```
5. To ensure that the driver pod has the necessary permissions to create and manage executor pods, we need to create a service account and assign it the appropriate roles.
Create a service account for Spark:

```bash
kubectl create serviceaccount spark-role -n spark
```
6. Grant the service account permissions to manage executor pods:
```bash
kubectl apply -f k8s/spark-role-binding.yaml
```
After this setup, the driver pod will have the necessary permissions to spawn executor pods within the spark namespace.

##  2. Creating the Driver Pod

To run or debug PySpark code directly from IDE in a Kubernetes environment, we need to create a **driver/dev pod**. This pod will serve as the development environment, allowing remote execution and debugging via IDE.

The driver pod is built from a Docker image created using the following steps:

- The **Dockerfile** ensures that the necessary Java version (**matching the version in the Kubernetes environment**) is installed.
- It installs the **Spark JARs** required to run Spark applications.
- An **SSH server** is set up to allow remote access.
- **Port 22** is exposed to facilitate SSH connections from the IDE for remote debugging.

The Dockerfile used to create the image is located in the project under ```dockerfiles/Dockerfile.devpod```. If there are any project-specific needs, you can update the Dockerfile, rebuild the image, and push it to the repository.

**To update the Driver Docker image:**
1. Update the `Dockerfile.devpod` as needed.
2. Build the updated Docker image:
```bash 
docker build -f kubernetes/Dockerfile.devpod -t xxxx/devpod:latest .
```
3. Push the updated image to the repository:
```bash 
docker push xxxxx/devpod:latest
```
I have already created and published this image, you can use it directly (`mervezeybel/devpod`).

To create the driver pod from this docker image use the `k8s/dev-pod.yaml`. In this file  the Docker image is specified, and the pod is configured to expose port 22 for SSH access.

**Steps:**
1. Use the k8s/dev-pod.yaml file to define the driver pod.
2. Deploy the driver pod by running the following command:
```bash 
`kubectl apply -f kubernetes/dev_pod.yaml -n spark
```
3. Check if the pod is running with the following command:
```bash 
`kubectl get pods -n spark
```
4. If the driver pod is not running, check its logs with the following command:
```bash 
`kubectl logs -n spark dev-pod
```
5. Once the pod is running, forward its port 22 to your local machine's port 2222 using the command below:
```bash 
kubectl port-forward dev-pod -n spark 2222:22
```

⚠️ **Note:** This command must remain active for continuous SSH access. If it stops, the connection will be lost.

6. To connect to the pod and interact with the development environment, run:
```bash 
kubectl exec -it dev-pod -n spark -- /bin/bash
```

## 3. Creating the Executor Docker Image

To run Spark code on Kubernetes, the executor container requires a specific Docker image, which is defined in the `dockerfiles/Dockerfile.executor` file. This image includes:

- **The same Spark version as the driver** (e.g., Spark 3.5.3) to ensure compatibility.
- **The same Java version as the Kubernetes environment** to avoid runtime issues.
- A working directory /app where the application files are copied.
- Python dependencies installed from requirements.txt.
- The main application entry point (main.py) to start the Spark job.

**To update the Executor Docker image:**
1. Update the `Dockerfile.executor` as needed.
2. Build the updated Docker image:
```bash 
docker build -f kubernetes/Dockerfile.executor -t xxxx/devpod:latest .
```
3. Push the updated image to the repository:
```bash 
docker push xxxx/executor:latest
```
I have already created and published this image, you can use it directly (`mervezeybel/executor`). 
This image will be used by the Spark executor pods when running your PySpark code on Kubernetes. Make sure that both the Spark and Java versions in the executor image match those in the driver pod to ensure smooth execution.

## 4. Configuring Spark for Execution

To run our code on Kubernetes, we need to specify the `Spark master` in `main.py`. Additionally, Spark's runtime parameters are defined in `configs/config.json`.

**Key Configurations** in `config.json`
- **Image Name:** If the default image is used, no changes are needed. However, if an updated image was built, its exact name should be specified.
- **Driver Host:** The Spark driver pod’s IP address must be provided for proper execution. Each time a new pod is created, its IP address will be different. Be sure to update this configuration accordingly.

**Retrieving the Driver Pod's IP Address**

   To get the **driver pod’s IP**, run the following command:
   ```bash 
    kubectl get pod dev-pod -n spark -o wide
   ```
   The **IP** column in the output contains the required **driver host IP**.
   
**Spark-Kubernetes Settings**: Update as needed
```json
 {
  "spark.kubernetes.namespace": "spark",
  "spark.kubernetes.container.image.pullPolicy": "IfNotPresent",
  "spark.kubernetes.authenticate.driver.serviceAccountName": "spark-role"
}
```
Other parameters in `config.json` can be modified based on project-specific requirements.

   ## 5 IDE Setup for Remote Execution (PyCharm)

Note: PyCharm was tested in this project, but a similar setup can be tried with VSCode."


1. Go to **Settings** → **Project: <project_name>** → **Python Interpreter**.
2. Select **Add Interpreter** → **On SSH**.
3. Enter the SSH details:
   - **Host:** localhost
   - **Port:** 2222
   - **Username:** devuser
   - **Password:** devuser
4. Click **Next**, set **Project Folder/Sync folders - Remote Path** to **/workspace**, and finalize the setup.
5. Install missing Python libraries if prompted.

Once inside in pode, you can find your code under the `/workspace` directory after setting up IDE (Pycharm/VSCode).
```bash 
kubectl exec -it dev-pod -n spark -- /bin/bash
cd /workspace
```
Everything is ready! Now you can run your code on Kubernetes by clicking the Run button or debug it by clicking the Debug button.
