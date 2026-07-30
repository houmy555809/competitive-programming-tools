import os, json

from . import common

class Workspace:
    def __init__(self, config):
        self.path = config.get("path", os.getcwd())

    def to_dict(self):
        return {
            "path": self.path
        }

def get_workspace():
    path = os.path.expanduser("~/.cpt/workspace.json")
    if not os.path.exists(path): return None
    config = json.load(open(path, "r"))
    return Workspace(config)

def _set_workspace(dir):
    workspace = get_workspace() or Workspace({})
    workspace.path = dir
    path = os.path.expanduser("~/.cpt/workspace.json")
    json.dump(workspace.to_dict(), open(path, "w"))

def set_workspace(args):
    path = args.target_dir or "."
    if args.use_workspace:
        workspace = workspace.get_workspace()
        if workspace is None:
            print("No workspace assigned. Please disable the -w/--workspace argument or assign a workspace with `cpt workspace`.")
            exit(0)
        path = os.path.join(workspace.path, path)
    path = os.path.abspath(path)
    _set_workspace(path)

def disable_workspace(args):
    path = os.path.expanduser("~/.cpt/workspace.json")
    if os.path.exists(path):
        os.remove(path)