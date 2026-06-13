Pod1 --> 10.244.0.7
Pod2 --> 10.244.0.8


eksctl create cluster --name demo-batch16a --region us-east-2 --nodegroup-name standard-workers --node-type t3.medium --nodes 2 --nodes-min 2 --nodes-max 3


aws eks --region us-east-2 update-kubeconfig --name demo-batch16a

eksctl delete cluster --name demo-batch16a --region us-east-2