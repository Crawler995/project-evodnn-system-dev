echo "" > ./result.txt

kubectl get nodes | awk '{print $1}' | grep -v "NAME" | xargs -I{} kubectl label node {} nvidia-device-enable=enable

for stage in inference; do
    for bs in 32; do
        # for p in 1.0 0.9 0.8 0.7 0.6 0.5 0.4 0.3 0.2 0.1; do
        for p in 1.0; do
            cp k3s-yaml/pod-template.yaml k3s-yaml/tmp-pod.yaml
            sed -i "s/DEFINE_GPU_ALLOC/$p/g" k3s-yaml/tmp-pod.yaml
            sed -i "s/DEFINE_BS/$bs/g" k3s-yaml/tmp-pod.yaml
            sed -i "s/DEFINE_STAGE/$stage/g" k3s-yaml/tmp-pod.yaml
            sed -i "s/DEFINE_RUN_ID/$stage-$bs-$p/g" k3s-yaml/tmp-pod.yaml
            sed -i "s/DEFINE_NUM_ITERATIONS/100/g" k3s-yaml/tmp-pod.yaml

            echo "----------------------------------------";
            cat k3s-yaml/tmp-pod.yaml | grep "kubeshare/gpu_request"
            cat k3s-yaml/tmp-pod.yaml | grep "kubeshare/gpu_limit"
            cat k3s-yaml/tmp-pod.yaml | grep "command"

            kubectl create -f k3s-yaml/tmp-pod.yaml
            # sleep 20s
            while [[ $(kubectl get pod | grep $stage-$bs-$p  | grep "Running") == "" ]]; do sleep 1s; echo "w"; done;

            echo "" >> ./result.txt
            echo $p >> ./result.txt
            kubectl logs -f $stage-$bs-$p >> ./result.txt

            kubectl delete -f k3s-yaml/tmp-pod.yaml
            echo "----------------------------------------";

            sleep 30s
        done
    done
done

rm k3s-yaml/tmp-pod.yaml
