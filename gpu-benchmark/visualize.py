import re 
import matplotlib.pyplot as plt
import yaml




BLUE = (45./255., 164./255., 205./255.)
GREEN = (1./255., 113./255., 0./255.)
YELLOW = (205/255., 194/255., 45/255.)
PURPLE = (204/255., 46/255., 206/255.)
GREY = (146./255., 146./255., 146./255.)
BLACK = (60./255., 60./255., 60./255.)
RED = (181./255., 23./255., 0./255.)



def read_yaml(p):
    with open(p, 'r') as f:
        return yaml.load(f, yaml.FullLoader)


datas_path_path = '/mnt/zql/k3s-kubeshare-gpu-allocation/gpu-benchmark/series_benchmark_logs/stage=inference|n_apps=1|bs=16|n_iters=200.txt'
with open(datas_path_path, 'r') as f:
    datas_path = f.read().split('\n')
datas_path = [p for p in datas_path if p != '']
datas = [read_yaml(p) for p in datas_path]
X = [data[0]['app_config']['resource_allocation'] for data in datas]
Y = [data[0]['app_perf']['latency'] for data in datas]
print(Y)
plt.plot(X, Y, label='inference', color=BLUE, lw=4, marker='o', markersize=10)
plt.grid()
plt.xlabel('GPU allocation')
plt.ylabel('Latency (ms)')
plt.legend()
plt.tight_layout()
plt.savefig(f'./tmp.png', dpi=300)
plt.clf()



datas_path_path = '/mnt/zql/k3s-kubeshare-gpu-allocation/gpu-benchmark/series_benchmark_logs/stage=training|n_apps=1|bs=16|n_iters=100.txt'
with open(datas_path_path, 'r') as f:
    datas_path = f.read().split('\n')
datas_path = [p for p in datas_path if p != '']
datas = [read_yaml(p) for p in datas_path]
X = [data[0]['app_config']['resource_allocation'] for data in datas]
Y = [data[0]['app_perf']['latency'] for data in datas]
print(Y)
plt.plot(X, Y, label='training', color=RED, lw=4, marker='o', markersize=10)
plt.grid()
plt.xlabel('GPU allocation')
plt.ylabel('Latency (ms)')
plt.legend()
plt.tight_layout()
plt.savefig(f'./tmp2.png', dpi=300)
plt.clf()
