import re 
import os
import subprocess 
import time 
import json

"""
ZEvent doesn't take extra information except event timestamp. 
We assume ZEvent is captured from logs of an app with known app_id.
"""
ZEVENT_TAGS = [
    "CONTAINER_RUN_STARTED",
    "INFERENCE_STARTED",
    "INFERENCE_ENDED",
    "TRAINING_STARTED",
    "TRAINING_ENDED",
    "CONTAINER_RUN_ENDED",
]


def get_cur_time_str():
    return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()))


def str_to_time(s, f='%Y-%m-%d %H:%M:%S'):
    if isinstance(s, time.struct_time):
        return s
    return time.strptime(s, f)


def time_to_str(t, f='%Y-%m-%d %H:%M:%S'):
    if isinstance(t, str):
        return t
    return time.strftime(f, time.localtime(time.mktime(t)))


def parse_zevents_timeline_from_log_file(log_file_path: str, time_save_format=str):
    assert time_save_format in [str, time.struct_time]

    zevents_timeline = [] # [(time, zevent_tag)]

    tmp_file_path = f'/tmp/{get_cur_time_str()}-zevents-tmp.txt'
    os.system(f'cat "{log_file_path}" | grep ZEVENT > "{tmp_file_path}"')
    with open(tmp_file_path, 'r') as f:
        related_log_lines = f.readlines()
    os.remove(tmp_file_path)

    timestamp_regx = re.compile(r'(\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)')
    event_tag_regx = re.compile(r'ZEVENT:([a-zA-Z_]+)')

    for log_line in related_log_lines:
        timestamp = timestamp_regx.findall(log_line)[0]
        timestamp = str_to_time(timestamp) if time_save_format == time.struct_time else timestamp
        zevent_tag = event_tag_regx.findall(log_line)[0]

        zevents_timeline += [(timestamp, zevent_tag)]
    zevents_timeline.sort(key=lambda i: i[0])
    return zevents_timeline


def convert_time_to_str_in_zevents_timeline(zevents_timeline):
    return [(time_to_str(i[0]), *i[1:]) for i in zevents_timeline]


def convert_str_to_time_in_zevents_timeline(zevents_timeline):
    return [(str_to_time(i[0]), *i[1:]) for i in zevents_timeline]


def merge_zevents_timelines(zevents_timelines, zevents_sources=None, normalize_start_to_0_sec=False):
    if zevents_sources is not None:
        assert len(zevents_timelines) == len(zevents_sources)

        merged_zevents_timelines = []
        for zevents_timeline, zevents_source in zip(zevents_timelines, zevents_sources):
            merged_zevents_timelines += [(timestamp, zevent_tag, zevents_source) for timestamp, zevent_tag in zevents_timeline]
        merged_zevents_timelines.sort(key=lambda i: i[0])
    else:
        merged_zevents_timelines = []
        for zevents_timeline in zevents_timelines:
            merged_zevents_timelines += zevents_timeline
        merged_zevents_timelines.sort(key=lambda i: i[0])

    if normalize_start_to_0_sec:
        merged_zevents_timelines = [(time.mktime(str_to_time(i[0])) - time.mktime(str_to_time(merge_zevents_timelines[0][0])), *i[1:])
                                    for i in merged_zevents_timelines]
    return merged_zevents_timelines


def save_zevents_timeline(zevents_timeline, fp):
    with open(fp, 'w') as f:
        json.dump(convert_time_to_str_in_zevents_timeline(zevents_timeline), f, indent=2)


def load_zevents_timeline(fp, time_format=str):
    assert time_format in [str, time.struct_time]
    with open(fp, 'r') as f:
        res = json.load(f)
    return res if time_format == str else convert_str_to_time_in_zevents_timeline(res)


def visualize_zevents_timeline(zevents_timeline, fig_save_path):
    pass
