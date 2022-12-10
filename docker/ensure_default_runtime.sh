if [[ $(cat /etc/docker/daemon.json | grep "nvidia-container-runtime") == "" ]]; then
    echo "[Note] Before this, make sure you have configured \"nvidia-container-runtime\" in your docker environment!!"
    exit 1
fi

if [[ $(cat /etc/docker/daemon.json | grep "\"default-runtime\": \"nvidia\"") == "" ]]; then
    echo "[Note] Before this, make sure \"default-runtime\": \"nvidia\" is added to /etc/docker/daemon.json!!"
    exit 1
fi

if [[ $(docker info | grep "Docker Root Dir") == " Docker Root Dir: /var/lib/docker" ]]; then
    echo "[Note] Before this, make sure you install Docker in a large disk instead of default root directory!!"
    exit 1
fi

echo "docker runtime check passed!"
