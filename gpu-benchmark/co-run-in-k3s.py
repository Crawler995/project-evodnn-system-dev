import re
import argparse
import time
import os
import subprocess
import yaml
import json
import matplotlib.pyplot as plt
from concurrent.futures import ThreadPoolExecutor


apps_run_id = {}


def get_cur_time_str():
    return time.strftime('%Y%m%d%H%M%S', time.localtime(time.time()))


def str_to_time(s, f='%Y-%m-%d %H:%M:%S'):
    return time.strptime(s, f)


def ensure_dir(fp):
    os.makedirs(os.path.dirname(fp), exist_ok=True)


class RunningEnv:
    def __init__(self, res_save_dir, apps_config, device):
        self.res_save_dir = res_save_dir
        self.launch_time_str = get_cur_time_str()
        for app_name, app_config in apps_config.items():
            app_config['name'] = app_name
        self.apps_config = apps_config
        self.apps_run_id = {app_name: self.get_app_run_id(app_config) for app_name, app_config in apps_config.items()}
        self.device = device

        self.app_log_files_type = {
            'config': 'json',
            'pod-config': 'yaml',
            'run-raw': 'log',
            'run': 'json',
            'launch-pod': 'sh',
            'resource-usage-raw': 'log',
            'resource-usage': 'json',
            'zevents': 'json'
        }
        self.running_env_log_files_type = {
            'vis-apps-resource-usage': 'png',
            'apps-zevents': 'json',
            'vis-apps-zevents': 'png'
        }

    def get_app_run_id(self, app_config):
        return app_config['name'] + '-' + self.launch_time_str

    """
    - <benchmark_log_name>
    - apps_logs
      - app_logs
        - config.json
        - pod-config.yaml
        - launch-pod.sh
        - run.log
        - resource-usage.log
        - zevents.json
    - vis-apps-resource-usage.png
    - apps-zevents.json
    - vis-apps-zevents.png
    """

    def get_app_log_file_path(self, app_name, log_type):
        assert log_type in self.app_log_files_type.keys()
        p = os.path.join(self.res_save_dir, f'./apps_logs/{app_name}/{log_type}.{self.app_log_files_type[log_type]}')
        ensure_dir(p)
        return p

    def get_running_env_log_file_path(self, log_type):
        assert log_type in self.running_env_log_files_type.keys()
        p = os.path.join(self.res_save_dir, f'{log_type}.{self.running_env_log_files_type[log_type]}')
        ensure_dir(p)
        return p

    def create_app_pod_run_id_and_config_file(self, app_name):
        run_id = self.apps_run_id[app_name]
        app_config = self.apps_config[app_name]

        with open('./k3s/pod-template.yaml', 'r') as f:
            content = f.read()

            content = content.replace('DEFINE_GPU_ALLOC_REQ', f'{max(0.05, app_config["resource_allocation"] - 0.0):.2f}')
            content = content.replace('DEFINE_GPU_ALLOC_LIMIT', f'{max(0.05, app_config["resource_allocation"] - 0.0):.2f}')
            content = content.replace('DEFINE_GPU_ALLOC', f'{app_config["resource_allocation"]:.2f}')
            content = content.replace('DEFINE_BS', f'{app_config["batch_size"]}')
            content = content.replace('DEFINE_STAGE', app_config['stage'])
            content = content.replace('DEFINE_RUN_ID', run_id)
            content = content.replace('DEFINE_NUM_ITERATIONS', f'{app_config["num_iterations"]}')

        pod_config_file = self.get_app_log_file_path(app_name, 'pod-config')
        with open(pod_config_file, 'w') as f:
            f.write(content)

    def create_app_pod_and_wait_it_until_finished(self, app_name):
        with open(self.get_app_log_file_path(app_name, 'config'), 'w') as f:
            json.dump(self.apps_config[app_name], f, indent=2)
        
        self.create_app_pod_run_id_and_config_file(app_name)
        app_pod_run_id, app_pod_config_file_path = self.apps_run_id[app_name], self.get_app_log_file_path(app_name, 'pod-config')
        log_file_path = self.get_app_log_file_path(app_name, 'run-raw')
        launch_app_bash_file_path = self.get_app_log_file_path(app_name, 'launch-pod')

        with open(launch_app_bash_file_path, 'w') as f:
            f.write(f'kubectl create -f {app_pod_config_file_path}\n')
            f.write('while [[ $(kubectl get pod | grep ' + app_pod_run_id + ' | grep "Running") == "" ]]; do sleep 1s; done;\n')
            f.write(f'echo "[app started] {app_pod_run_id}"\n')
            f.write(f'echo "[app logs location] {log_file_path}"\n')
            f.write(f'kubectl logs -f {app_pod_run_id} > {log_file_path}\n')
            f.write(f'kubectl delete -f {app_pod_config_file_path}\n')
            f.write('while [[ $(kubectl get pod | grep ' + app_pod_run_id + ' ) != "" ]]; do sleep 1s; done;\n')
            f.write(f'echo "[app killed] {app_pod_run_id}"\n')
        os.system(f'/bin/bash {launch_app_bash_file_path}')

    def get_and_save_app_perf_from_app_pod_log(self, app_name):
        app_pod_log_file_path = self.get_app_log_file_path(app_name, 'run-raw')
        with open(app_pod_log_file_path, 'r') as f:
            content = f.read()

        regx = re.compile(r'latency: (.+?) \(ms\)')
        latency = float(regx.findall(content)[0])
        perf = dict(latency=latency)

        with open(self.get_app_log_file_path(app_name, 'run'), 'w') as f:
            json.dump(perf, f, indent=2)

    def get_and_save_app_gpu_usage_from_kubeshare_log(self, app_name):
        app_run_id = self.apps_run_id[app_name]
        tmp_gpu_usage_log_file_path = self.get_app_log_file_path(app_name, 'resource-usage-raw')

        os.system("kubectl get pod -A | grep node-daemon | awk '{print $2}' | "
                "xargs -I{} kubectl logs {} -c gemini-scheduler -n kube-system | grep \"" + app_run_id + "\" | grep \"GPU usage\" > " + tmp_gpu_usage_log_file_path)

        with open(tmp_gpu_usage_log_file_path, 'r') as f:
            gpu_usage_log = f.read()
        
        app_time_gpu_usage_regx = re.compile(r'(.+?)\.\d{6} INFO.+?GPU usage: (.+?),')
        app_time_gpu_usage_info = app_time_gpu_usage_regx.findall(gpu_usage_log)
        app_time_gpu_usage_info_for_dump = [(i[0], float(i[1])) for i in app_time_gpu_usage_info]
        with open(self.get_app_log_file_path(app_name, 'resource-usage'), 'w') as f:
            json.dump(app_time_gpu_usage_info_for_dump, f, indent=2)

    def get_and_save_app_resource_usage(self, app_name):
        if self.device == 'cuda':
            self.get_and_save_app_gpu_usage_from_kubeshare_log(app_name)

    def get_and_save_app_zevents(self, app_name):
        related_log_files = [self.get_app_log_file_path(app_name, k)
                             for k in self.app_log_files_type.keys() if 'zevent' not in k]
        from zevent_parser import parse_zevents_timeline_from_log_file, merge_zevents_timelines, save_zevents_timeline
        zevents_timelines = [parse_zevents_timeline_from_log_file(f) for f in related_log_files]
        merged_zevents_timeline = merge_zevents_timelines(zevents_timelines)
        save_zevents_timeline(merged_zevents_timeline, self.get_app_log_file_path(app_name, 'zevents'))

    def benchmark_an_app_pipepine(self, app_name):
        self.create_app_pod_and_wait_it_until_finished(app_name)
        self.get_and_save_app_perf_from_app_pod_log(app_name)
        self.get_and_save_app_resource_usage(app_name)
        self.get_and_save_app_zevents(app_name)

    def benchmark_pipeline(self):
        print('benchmark start...')
        with ThreadPoolExecutor() as pool:
            for _ in pool.map(self.benchmark_an_app_pipepine, list(self.apps_config.keys())):
                pass
        print('benchmark finished!')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--num_co_running_apps', type=int)
    parser.add_argument('--batch_size', type=int)
    parser.add_argument('--resource_allocation_per_app', type=float)
    parser.add_argument('--stage', type=str, choices=['inference', 'training'])
    parser.add_argument('--num_iterations', type=int, default=100)
    parser.add_argument('--write_benchmark_res_file_path_to', type=str, default='')
    args = parser.parse_args()

    apps_config = {
        f'app-{index}': dict(batch_size=args.batch_size, resource_allocation=args.resource_allocation_per_app, 
        stage=args.stage, num_iterations=args.num_iterations)
        for index in range(args.num_co_running_apps)
    }
    for app_index, app_config in enumerate(apps_config):
        print(f'{app_index}-th app | config: {app_config}')

    running_env = RunningEnv(f'./running_env_logs/{get_cur_time_str()}', apps_config, 'cuda')
    running_env.benchmark_pipeline()

    # benchmarks_res_file_path = f'./benchmark_logs/{get_cur_time_str()}/res.yaml'
    # os.makedirs(os.path.dirname(benchmarks_res_file_path), exist_ok=True)
    # with open(benchmarks_res_file_path, 'w') as f:
    #     yaml.dump(benchmarks_res, f)
    
    # for an_app_benchmark_res in benchmarks_res:
    #     app_index = an_app_benchmark_res['app_config']['index']
    #     app_gpu_usage_info = an_app_benchmark_res['app_gpu_usage']
    #     X, Y = [i[0] for i in app_gpu_usage_info], [i[1] for i in app_gpu_usage_info]
    #     X = [time.mktime(i) - time.mktime(X[0]) for i in X]
    #     print(X, Y)
    #     plt.plot(X, Y, label=f'app {app_index}')
    # plt.xlabel('Time')
    # plt.ylabel('GPU Usage')
    # plt.grid()
    # plt.legend()
    # plt.tight_layout()
    # plt.savefig(os.path.join(os.path.dirname(benchmarks_res_file_path), 'apps-gpu-usage.png'))
    # plt.clf()

    # print(f'benchmark res is saved in {os.path.abspath(benchmarks_res_file_path)}')

    # if args.write_benchmark_res_file_path_to != '':
    #     os.makedirs(os.path.dirname(args.write_benchmark_res_file_path_to), exist_ok=True)
    #     with open(args.write_benchmark_res_file_path_to, 'a') as f:
    #         f.write(os.path.abspath(benchmarks_res_file_path) + '\n')
    #     print(f'the location of benchmark res is appended into {os.path.abspath(args.write_benchmark_res_file_path_to)}')
    