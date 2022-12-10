set -e

echo "----------------"
echo "KubeShare for NVIDIA Jetson devices"
echo "Based on KubeShare 1.0 (https://github.com/NTHU-LSALAB/KubeShare/tree/release-1.0)"
echo "Modified by queyu, 2022.12"
echo "----------------"

if [[ $(pwd | grep "kubeshare-arm64") == "" ]]; then
    echo "[Error] Run this script under \"kubeshare-arm64\" directory!"
    exit 1
fi

echo "[Note] This repo is modified for ARM64 CUDA10.2 NVIDIA Jetson devices (by making specific Makefile/Dockerfile and mocking NVML library) and not applicable in x86 platforms."
if [[ $(uname -m) != "aarch64" ]]; then
    echo "[Error] not-ARM64 device detected (your device is $(uname -m) based)!"
    exit 1
fi

echo -e "\033[1;31;34m[Note] Before building, please modify GPU total memory (B) in KubeShare-release-1.0/pkg/configclient/config-client.go:L82 !\033[m"
echo -e "\033[1;31;34m[Note] Current value:\033[m"
cat KubeShare-release-1.0/pkg/configclient/config-client.go | grep "DEFINE_TOTAL_MEMORY"

echo -e "\033[1;31;34m[Note] Before building, you can adjust QUOTA, MIN_QUOTA, and WINDOW_SIZE in KubeShare-release-1.0/docker/kubeshare-gemini-scheduler/launcher.py. According to the original paper, the user program will reach the GPU utilization limitation in ~20 seconds from it starts. Actually this is a little long for fast edge re-training. So I think aforementioned arguments may should be less.\033[m"
echo -e "\033[1;31;34m[Note] Current value:\033[m"
cat KubeShare-release-1.0/docker/kubeshare-gemini-scheduler/launcher.py | grep "\-\-base_quota"
cat KubeShare-release-1.0/docker/kubeshare-gemini-scheduler/launcher.py | grep "\-\-min_quota"
cat KubeShare-release-1.0/docker/kubeshare-gemini-scheduler/launcher.py | grep "\-\-window"

echo "[Note] Archived Gemini-v1.0 source code (with minor revision) is used in docker building instead of git clone the default Gemini repo."

sleep 5s

bash ../util/launch_local_docker_hub.sh

cd KubeShare-release-1.0
cp Makefile-arm64 Makefile

# for d in kubeshare-config-client kubeshare-device-manager kubeshare-gemini-hook-init kubeshare-gemini-scheduler kubeshare-scheduler kubeshare-vgpupod; do
for d in kubeshare-gemini-scheduler; do
    echo -e "\033[1;31;34m[Note] $d building...\033[m"
    
    docker build -f docker/$d/Dockerfile-arm64 -t $d .

    docker tag $d:latest 127.0.0.1:5000/$d:latest
    docker push 127.0.0.1:5000/$d:latest

    echo -e "\033[1;31;34m[Note] $d building finished!\033[m"
done

rm Makefile
cd ..
bash ../util/rm-none-docker-images.sh 

echo "[Note] Built and pushed images:"
docker images | grep 127.0.0.1:5000/kubeshare
