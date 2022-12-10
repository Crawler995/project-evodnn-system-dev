echo "Run built image in docker..."

docker run --gpus all -it 127.0.0.1:5000/zql-gpu-benchmark:latest python3 -u gpu-benchmark.py \
    --batch_size 16 \
    --stage training \
    --resource_allocation 1.0 \
    --num_iterations 100