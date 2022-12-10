if [[ $(cat /etc/docker/daemon.json | grep "127.0.0.1:5000") == "" ]]; then
    echo "[Note] Before this, make sure \"insecure-registries\": [\"127.0.0.1:5000\"] is added to /etc/docker/daemon.json!!"
    exit 1
fi

if [[ $(docker ps | grep "registry") != "" ]]; then
    echo "[Note] docker.io/registry has already launched."
    exit 0
fi

echo "[Note] Launching docker.io/registry in 127.0.0.1:5000 ..."
sudo docker pull docker.io/registry
sudo docker run -d -p 5000:5000 --name=registry --restart=always --privileged=true registry

./restart-docker.sh
