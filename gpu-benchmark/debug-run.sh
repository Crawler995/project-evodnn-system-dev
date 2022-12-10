kubectl get nodes | awk '{print $1}' | grep -v "NAME" | xargs -I{} kubectl label node {} nvidia-device-enable=enable
kubectl create -f k3s-yaml/tmp-pod.yaml

while [[ $(kubectl get pod | grep "inference-32-1.0"  | grep "Running") == "" ]]; do sleep 1s; echo "w"; done;

kubectl logs -f inference-32-1.0
kubectl delete -f k3s-yaml/tmp-pod.yaml
