import json
import os
import shutil
import sys
import uuid
from datetime import datetime

from . import workspace

ROOT = os.path.expanduser("~")
CACHE_DIR = os.path.join(ROOT, ".cpt", "cache")

os.makedirs(CACHE_DIR, exist_ok = True)

task_id = str(uuid.uuid4())
task_folder = os.path.join(CACHE_DIR, task_id)


def check_create_cache_file():
    if not os.path.exists(task_folder):
        os.makedirs(task_folder)
        with open(os.path.join(task_folder, "meta.json"), "w", encoding = "utf-8") as f:
            json.dump({
                "time": str(datetime.now()),
                "argv": sys.argv
            }, f)


def dump_file(folder, name, content):
    check_create_cache_file()
    cur_folder = os.path.join(task_folder, folder)
    if not os.path.exists(cur_folder):
        os.mkdir(cur_folder)
    filename = os.path.join(cur_folder, name)
    with open(filename, "w", encoding = "utf-8") as f:
        f.write(content)
    return filename


class CacheFolderReader:
    def __init__(self, path):
        if path.endswith("/"):
            path = path[:-1]
        self.path = path
        self.uuid = path.split("/")[-1]
        with open(os.path.join(path, "meta.json"), "r", encoding = "utf-8") as f:
            self.data = json.load(f)
        self.created_time_str = self.data["time"]
        self.created_time = datetime.strptime(self.data["time"], "%Y-%m-%d %H:%M:%S.%f")
        self.argv = self.data["argv"]

    def show(self):
        print(f"{self.uuid:<40}{self.created_time_str:<40}{' '.join(self.argv[1:])}")


def _get_cached_folders():
    _, folders, _ = next(os.walk(CACHE_DIR))
    readers = []
    for folder in folders:
        readers.append(CacheFolderReader(os.path.join(CACHE_DIR, folder)))
    readers.sort(key = lambda x: x.created_time, reverse = True)
    return readers


def list_files(args):
    num = args.num
    print(f"{'Cache ID':<40}{'Creation Time':<40}Shell Parameters")
    for reader in _get_cached_folders()[:num]:
        reader.show()


def purge():
    for reader in _get_cached_folders():
        shutil.rmtree(reader.path)


def recover(args):
    readers = _get_cached_folders()

    if args.cache_id is None:
        if not readers:
            print("Nothing to recover.")
            return
        reader = readers[0]
    else:
        target_path = os.path.join(CACHE_DIR, args.cache_id)
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
