import torch
import torch.cuda
import os
import sys
import torchvision
import time
import numpy as np
# import tqdm
import argparse
# from tqdm import trange
from lw_resnet18 import ResNet56_cifar
from typing import Tuple


def get_cur_time_str():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def log_zevent(zevent_tag):
    print(f'{get_cur_time_str()} ZEVENT:{zevent_tag}')


def get_model_latency(model: torch.nn.Module, model_input_size: Tuple[int, int, int, int], sample_num: int, 
                      device: str):

    log_zevent('INFERENCE_STARTED')

    dummy_input = torch.rand(model_input_size).to(device)
    model = model.to(device)
    model.eval()

    def _infer(tag):
        # print(f'{tag}...')
        with torch.no_grad():
            # for i in trange(sample_num, desc=f'{tag}...'):
            for i in range(sample_num):
                print(f'infer {tag} {i}')
                model(dummy_input)
    
    # warm up
    # _infer('warm up')

    start = time.time()

    _infer('inferring')

    log_zevent('INFERENCE_ENDED')

    latency = time.time() - start
    return latency / sample_num
       
    # if device == 'cuda' or 'cuda' in str(device):
    #     s, e = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    #     s.record()
    #     _infer(f'inferring on {device}')
    #     e.record()
    #     torch.cuda.synchronize()
    #     total_latency = s.elapsed_time(e) / 1000.

    # else:
    #     start = time.time()
    #     _infer(f'inferring on {device}')
    #     total_latency = time.time() - start

    # total_latency /= sample_num
                
    # return total_latency


def get_model_training_time(model: torch.nn.Module, model_input_size: Tuple[int, int, int, int], sample_num: int, 
                      device: str):

    log_zevent('TRAINING_STARTED')

    dummy_input = torch.rand(model_input_size).to(device)
    model = model.to(device)

    def _train(tag):
        # print(f'{tag}...')
        optimizer = torch.optim.SGD(model.parameters(), lr=1e-5)
        # for i in trange(sample_num, desc=f'{tag}...'):
        for i in range(sample_num):
            print(f'train {tag} {i}')
            model.train()
            o = model(dummy_input)
            loss = (o ** 2).sum()

            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
    
    # warm up
    # _train('warm up')

    s = time.time()

    _train('training')

    log_zevent('TRAINING_ENDED')

    latency = time.time() - s
    return latency / sample_num
       
    # if device == 'cuda' or 'cuda' in str(device):
    #     s, e = torch.cuda.Event(enable_timing=True), torch.cuda.Event(enable_timing=True)
    #     s.record()
    #     _train(f'trainig on {device}')
    #     e.record()
    #     torch.cuda.synchronize()
    #     total_latency = s.elapsed_time(e) / 1000.

    # else:
    #     start = time.time()
    #     _train(f'trainig on {device}')
    #     total_latency = time.time() - start
    
    # total_latency /= sample_num
    # return total_latency


parser = argparse.ArgumentParser()
parser.add_argument('--batch_size', type=int)
parser.add_argument('--num_iterations', type=int)
parser.add_argument('--resource_allocation', type=float)
parser.add_argument('--stage', type=str, choices=['inference', 'training'])
args = parser.parse_args()

# class Args:
#     def __init__(self):
#         self.stage = 'inference'
#         self.batch_size = 1
#         self.num_iterations = 100
# args = Args()

print('Library version:')
print('-' * 20)
print('Python version: ', sys.version.split(' ')[0])
print('PyTorch version: ', torch.__version__)
print('torchvision version: ', torchvision.__version__)
print('torch CUDA available: ', torch.cuda.is_available())
print('CUDA version: ', torch.version.cuda)
print('CuDNN version: ', torch.backends.cudnn.version())
print('-' * 20)

print('loading ResNet-56 (32*32)...')
model = ResNet56_cifar()
print('ResNet-56 loaded')
print('Send model to GPU...')
model = model.cuda()
print('Send finsihed')
print('Model inference trial...')
model(torch.rand((1, 3, 32, 32), device='cuda'))
print('Model inference trial finished')

print(f'start profiling {args.stage}...')
bs = args.batch_size


# s = time.time()

# NOTE: I don't know why latency measured by torch.cuda.Event() is not correct (the error is too large)
# so simply use time.time() in the outside instead of it
if args.stage == 'inference':
    latency = get_model_latency(model, (bs, 3, 32, 32), args.num_iterations, 'cuda')
else:
    latency = get_model_training_time(model, (bs, 3, 32, 32), args.num_iterations, 'cuda')

# latency = time.time() - s
latency *= 1000.

print(f'batch size = {bs}, stage = {args.stage}, resource allocation: {args.resource_allocation:.2f} | latency: {latency:.4f} (ms)')
