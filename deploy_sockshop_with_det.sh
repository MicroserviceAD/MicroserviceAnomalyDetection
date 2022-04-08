#!/bin/sh
#  Deploys sock-shop, assumes minikube has started
kubectl create namespace sock-shop
kubectl apply -f ./sockshop_modified_full_cluster_with_det.yaml