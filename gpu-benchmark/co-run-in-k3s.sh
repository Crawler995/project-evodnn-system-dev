batch_size=16
num_iterations=200

# co-running apps: 1
num_co_running_apps=1
for stage in training; do
    # write_benchmark_res_file_path_to="./series_benchmark_logs/stage=$stage|n_apps=$num_co_running_apps|bs=$batch_size|n_iters=$num_iterations.txt"
    # echo "" > $write_benchmark_res_file_path_to

    # echo "dummy benchmark for warm up..."
    python3 co-run-in-k3s.py \
        --num_co_running_apps $num_co_running_apps \
        --batch_size $batch_size \
        --resource_allocation_per_app 0.5 \
        --stage $stage \
        --num_iterations $num_iterations

    # for resource_allocation in 0.1 0.2 0.3 0.4 0.5 0.6 0.7 0.8 0.9 1.0; do
    #     python3 co-run-in-k3s.py \
    #         --num_co_running_apps $num_co_running_apps \
    #         --batch_size $batch_size \
    #         --resource_allocation_per_app $resource_allocation \
    #         --stage $stage \
    #         --num_iterations $num_iterations 
            # --write_benchmark_res_file_path_to $write_benchmark_res_file_path_to
    # done
done
