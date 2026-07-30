from enum import Enum
from colorama import *
import os
import shutil
from datetime import datetime
import uuid
import json
import sys

from . import common, workspace

root = os.path.expanduser("~")

if not os.path.exists(root + "/.cpt"): os.mkdir(root + "/.cpt")
if not os.path.exists(root + "/.cpt/cache"): os.mkdir(root + "/.cpt/cache")

folder_name = root + "/.cpt/cache/"

task_id = str(uuid.uuid4())
task_folder = os.path.join(folder_name, task_id)

def check_create_cache_file():
    global task_id, task_folder
    if not os.path.exists(task_folder):
        os.mkdir(task_folder)
        json.dump({
            "time": str(datetime.now()),
            "argv": sys.argv
        }, open(os.path.join(task_folder, "meta.json"), "w"))

def dump_file(folder, name, content):
    global task_folder
    check_create_cache_file()
    cur_folder = os.path.join(task_folder, folder)
    if not os.path.exists(cur_folder):
        os.mkdir(cur_folder)
    filename = os.path.join(cur_folder, name)
    open(filename, "w", encoding = "utf-8").write(content)
    return filename

class CacheFolderReader:
    def __init__(self, path):
        if path.endswith("/"): path = path[:-1]
        self.path = path
        self.uuid = self.path.split("/")[-1]
        self.data = json.load(open(os.path.join(path, "meta.json"), "r"))
        self.createdTimeStr = self.data["time"]
        self.createdTime = datetime.strptime(self.data["time"], "%Y-%m-%d %H:%M:%S.%f")
        self.argv = self.data["argv"]

    def print(self):
        print("%-40s%-40s%s" % (self.uuid, self.createdTimeStr, ' '.join(self.argv[1:])))

def _get_cached_folders():
    base_path = root + "/.cpt/cache"
    _, folders, _ = next(os.walk(base_path))
    readers = []
    for folder in folders:
        readers.append(CacheFolderReader(os.path.join(base_path, folder)))
    readers.sort(key = lambda x: x.createdTime, reverse = True)
    return readers

def list_files(args):
    num = args.num
    base_path = root + "/.cpt/cache"
    print("%-40s%-40s%s" % ("Cache ID", "Creation Time", "Shell Parameters"))
    for reader in _get_cached_folders()[:num]:
        reader.print()

def purge():
    base_path = root + "/.cpt/cache"
    for reader in _get_cached_folders():
        shutil.rmtree(reader.path)

def recover(args):
    base_path = root + "/.cpt/cache"
    readers = _get_cached_folders()

    if args.cache_id is None:
        if not readers:
            print(f"Nothing to recover.")
            return
        reader = readers[0]
    else:
        target_path = os.path.join(base_path, args.cache_id)
        if not os.path.exists(target_path):
            print(f"Cache '{args.cache_id}' not found.")
            return
        reader = CacheFolderReader(target_path)

    target_dir = args.output
    if args.use_workspace:
        cur_workspace = workspace.get_workspace()
        if cur_workspace is None:
            print("No workspace assigned. Please disable the -w/--workspace argument or assign a workspace with `cpt workspace`.")
            exit(0)
        target_dir = os.path.join(cur_workspace.path, target_dir)
    target_dir = os.path.abspath(target_dir)
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    for item in os.listdir(reader.path):
        if item == "meta.json":
            continue
        src = os.path.join(reader.path, item)
        dst = os.path.join(target_dir, item)
        if os.path.isdir(src):
            shutil.copytree(src, dst, dirs_exist_ok = True)
        else:
            shutil.copy2(src, dst)

    print(f"Cache '{reader.uuid}' recovered to {target_dir}")