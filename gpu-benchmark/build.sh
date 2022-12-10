set -e

cd src

# mkdir usr_lib_aarch64_tegra
# mkdir usr_local_cuda_targets_lib
# mkdir usr_lib_aarch64
# mkdir usr_local_cuda_lib64

# echo "copy critical library files..."
# Gemini build needs `$(CUDA_PATH)/lib64 -L$(CUDA_PATH)/lib64/stubs`

# for lib in libcuda.so.1.1 libnvrm_gpu.so libnvrm.so libnvrm_graphics.so libnvidia-fatbinaryloader.so.440.18 libnvos.so; do
#     cp /usr/lib/aarch64-linux-gnu/tegra/$lib ./usr_lib_aarch64_tegra
# done
# for lib in libcurand.so* libcufft.so* libcusparse.so* libcusolver.so*; do
#     cp /usr/local/cuda/targets/aarch64-linux/lib/$lib ./usr_local_cuda_targets_lib
# done
# for lib in libcublas.so* libcudnn.so* libcublasLt.so*; do
#     cp /usr/lib/aarch64-linux-gnu/$lib ./usr_lib_aarch64
# done
# # for lib in libcudart.so* libnvToolsExt.so*; do
# #     cp /usr/local/cuda/lib64/$lib ./usr_local_cuda_lib64
# # done
# cp -r /usr/local/cuda/lib64/* usr_local_cuda_lib64
# cp /usr/local/cuda/targets/aarch64-linux/lib/lib* ./usr_local_cuda_targets_lib
# cp -r /usr/local/cuda/targets/aarch64-linux/lib/stubs ./usr_local_cuda_targets_lib
# cp /usr/lib/aarch64-linux-gnu/libcu* ./usr_lib_aarch64

echo "ARCH: $ARCH"
docker build -f Dockerfile-$ARCH -t zql-gpu-benchmark .

# rm -r usr_lib_aarch64_tegra
# rm -r usr_local_cuda_targets_lib
# rm -r usr_lib_aarch64
# rm -r usr_local_cuda_lib64

cd ../../docker
bash launch-local-docker-hub.sh

docker tag zql-gpu-benchmark:latest 127.0.0.1:5000/zql-gpu-benchmark:latest
docker push 127.0.0.1:5000/zql-gpu-benchmark:latest

bash rm-none-docker-images.sh

docker images | grep 127.0.0.1:5000/zql-gpu-benchmark
