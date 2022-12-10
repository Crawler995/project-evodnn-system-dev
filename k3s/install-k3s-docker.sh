# https://docs.rancher.cn/docs/k3s/installation/install-options/_index

# curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn INSTALL_K3S_VERSION=v1.25.4+k3s1 sh -
# set -e

echo "install k3s with docker"

# curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn INSTALL_K3S_VERSION=v1.19.4+k3s1 sh -s - --docker --disable-agent

# 1.18.12+k3s1

mkdir -p /mnt/zql/k3s/bin
mkdir -p /mnt/zql/k3s/systemd

curl -sfL https://rancher-mirror.oss-cn-beijing.aliyuncs.com/k3s/k3s-install.sh | INSTALL_K3S_MIRROR=cn \
    INSTALL_K3S_VERSION=v1.18.12+k3s1 \
    INSTALL_K3S_BIN_DIR=/mnt/zql/k3s/bin \
    INSTALL_K3S_SYSTEMD_DIR=/mnt/zql/k3s/systemd \
    INSTALL_K3S_EXEC="--kubelet-arg eviction-hard=nodefs.available<5Gi --kubelet-arg eviction-hard=imagefs.available<5Gi" \
    sh -s - --docker

sudo chmod 777 /etc/rancher/k3s/k3s.yaml
sudo ln -s /mnt/zql/k3s/bin/kubectl /usr/local/bin/kubectl
