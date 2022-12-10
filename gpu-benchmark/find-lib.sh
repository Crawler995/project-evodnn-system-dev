for d in /usr/lib/aarch64-linux-gnu/tegra /usr/local/cuda/targets/aarch64-linux/lib /usr/lib/aarch64-linux-gnu /usr/local/cuda/lib64; do
    echo $d
    ls -lh $d | grep $1
done