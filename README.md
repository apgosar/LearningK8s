# Kubernetes Training Notes

This repository contains Kubernetes examples for Batch 16A, including simple root
manifests and a three-tier Flask/PostgreSQL learning app under `sessions/`.

## Current EKS Version

As of 2026-06-13, the latest Amazon EKS Kubernetes version in standard support is
`1.36`.

Reference:

```text
https://docs.aws.amazon.com/eks/latest/userguide/kubernetes-versions.html
```

Before creating a cluster in the future, check the versions currently available
in your AWS account and region:

```bash
aws eks describe-cluster-versions --region us-east-2
```

## Prerequisites

Install and configure these tools before creating the cluster:

- AWS CLI v2
- `eksctl`
- `kubectl`
- An AWS IAM user or role with permissions to create EKS, EC2, VPC, IAM, and
  load balancer resources

Confirm AWS access:

```bash
aws sts get-caller-identity
```

## Create The EKS Cluster

The original notes used the cluster name `demo-batch16a` in `us-east-2`. This
README keeps the same values and adds the latest EKS version.

```bash
export CLUSTER_NAME=demo-batch16a
export AWS_REGION=us-east-2
export EKS_VERSION=1.36

eksctl create cluster \
  --name "$CLUSTER_NAME" \
  --region "$AWS_REGION" \
  --version "$EKS_VERSION" \
  --nodegroup-name standard-workers \
  --node-type t3.medium \
  --nodes 2 \
  --nodes-min 2 \
  --nodes-max 3
```

This creates:

- An EKS control plane running Kubernetes `1.36`
- A managed node group named `standard-workers`
- Two `t3.medium` worker nodes, autoscaling between two and three nodes
- AWS networking resources required by the cluster

## Configure kubectl

```bash
aws eks --region "$AWS_REGION" update-kubeconfig --name "$CLUSTER_NAME"
```

Verify access:

```bash
kubectl version
kubectl get nodes
kubectl get namespaces
```

## Deploy The Root Nginx Example

From the repository root:

```bash
kubectl apply -f namespace-pk.yml
kubectl apply -f deployment-pk.yml
kubectl apply -f service-pk.yml
```

Check the workload:

```bash
kubectl get all -n pk
kubectl get service nginx-service -n pk
```

The `nginx-service` is a `LoadBalancer` service. On EKS, AWS provisions an
external load balancer for it. Wait until the `EXTERNAL-IP` or hostname appears,
then open it in a browser.

Cleanup the root example:

```bash
kubectl delete -f service-pk.yml --ignore-not-found
kubectl delete -f deployment-pk.yml --ignore-not-found
kubectl delete -f namespace-pk.yml --ignore-not-found
```

## Run The Training Sessions

Session guides are available in:

```text
sessions/01-core-k8s/README.md
sessions/02-storage-pv-pvc-statefulset/README.md
```

Session 01 covers core Kubernetes objects:

```bash
cd sessions/01-core-k8s
kubectl apply -f subsessions/01-namespace/
kubectl apply -f subsessions/02-configmap-secret/
kubectl apply -f subsessions/03-postgres-deployment-service/
kubectl apply -f subsessions/05-flask-deployment/
kubectl apply -f subsessions/06-flask-services/01-flask-service-clusterip.yml
```

Session 02 covers persistent storage, PVCs, StorageClass, and StatefulSet:

```bash
cd sessions/02-storage-pv-pvc-statefulset
kubectl apply -f subsessions/01-storage-problem-and-shared-config/
kubectl apply -f subsessions/02-static-pv-pvc/
kubectl apply -f subsessions/03-postgres-with-static-pvc/
kubectl apply -f subsessions/04-flask-with-persistent-db/
```

For the dynamic EBS StorageClass example in Session 02, the cluster also needs
the Amazon EBS CSI driver installed.

## Delete The EKS Cluster

Delete application resources first, then delete the cluster:

```bash
eksctl delete cluster --name "$CLUSTER_NAME" --region "$AWS_REGION"
```

If you did not keep the environment variables from earlier:

```bash
eksctl delete cluster --name demo-batch16a --region us-east-2
```

EKS clusters, worker nodes, EBS volumes, and load balancers can create AWS
charges while they exist. Delete the cluster when the lab is finished.
