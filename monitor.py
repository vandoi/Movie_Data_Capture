#!/usr/bin/env python3
import argparse
import os
import shutil
import time

# Monitor
from watchdog.observers import Observer
from watchdog.events import PatternMatchingEventHandler

# AV_Data_capture
import config
import AV_Data_Capture

def argparse_function() -> [str]:
    parser = argparse.ArgumentParser()
    parser.add_argument("-c", "--config", default='config.ini', nargs='?', help="The config file Path.")
    args = parser.parse_args()
    return args.config

def _safe_move(src, target):
    if os.path.exists(target):
        raise FileExistsError()
    else:
        shutil.move(src, target)

def _run_data_capture():
    AV_Data_Capture.main(conf)

def on_normal_created(event):
    filename = os.path.basename(event.src_path)
    target_path = os.path.join(data_path, filename)

    print("[Monitor] normal video: {} => {}".format(event.src_path, target_path))
    conf.get_inside_conf().set("common", "multi_part_abc", "0")
    print("[Monitor] multi_part_abc: {}".format(conf.multi_part_abc()))
    _safe_move(event.src_path, target_path)
    _run_data_capture()

def on_vr_created(event):
    filename = os.path.basename(event.src_path)
    target_path = os.path.join(data_path, filename)

    print("[Monitor] vr video: {} => {}".format(event.src_path, target_path))
    conf.get_inside_conf().set("common", "multi_part_abc", "1")
    print("[Monitor] multi_part_abc: {}".format(conf.multi_part_abc()))
    _safe_move(event.src_path, target_path)
    _run_data_capture()

# def on_deleted(event):
#     print("what the f**k! Someone deleted {}!".format(event.src_path))

# def on_modified(event):
#     print("hey buddy, {} has been modified".format(event.src_path))

# def on_moved(event):
#     print("ok ok ok, someone moved {} to {}".format(event.src_path, event.dest_path))

if __name__ == "__main__":
    patterns = [
        "*.iso","*.ISO","*.AVI","*.RMVB","*.WMV","*.MOV",
        "*.MP4","*.MKV","*.FLV","*.TS","*.WEBM","*.avi",
        "*.rmvb","*.wmv","*.mov","*.mp4","*.mkv","*.flv",
        "*.ts","*.webm"
    ]
    ignore_patterns = ""
    ignore_directories = False
    case_sensitive = True

    # Parse arguments
    config_file = argparse_function()

    # Read config.ini
    conf = config.Config(path=config_file)

    # Create the event handler and register the handling functions
    normal_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    normal_handler.on_created = on_normal_created

    vr_handler = PatternMatchingEventHandler(patterns, ignore_patterns, ignore_directories, case_sensitive)
    vr_handler.on_created = on_vr_created

    # event_handler.on_deleted = on_deleted
    # event_handler.on_modified = on_modified
    # event_handler.on_moved = on_moved

    # Start the monitor
    normal_path = conf.monitor_normal_dir()
    vr_path = conf.monitor_vr_dir()
    data_path = conf.monitor_data_dir()
    go_recursively = conf.monitor_is_recursive()

    print("[Monitor] data path: {}".format(data_path))
    normal_observer = None
    if normal_path != "":
        print("[Monitor] normal path: {}".format(normal_path))
        normal_observer = Observer()
        normal_observer.schedule(normal_handler, normal_path, recursive=go_recursively)
        normal_observer.start()

    vr_observer = None
    if vr_path != "":
        print("[Monitor] vr path: {}".format(vr_path))
        vr_observer = Observer()
        vr_observer.schedule(vr_handler, vr_path, recursive=go_recursively)
        vr_observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        if normal_observer != None:
            normal_observer.stop()
            normal_observer.join()
        if vr_observer != None:
            vr_observer.stop()
            vr_observer.join()
