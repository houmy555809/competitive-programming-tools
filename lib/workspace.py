import json
import os


class Workspace:
    def __init__(self, config):
        self.path = config.get("path", os.getcwd())

    def to_dict(self):
        return {
            "path": self.path
        }


def get_workspace():
    path = os.path.expanduser("~/.cpt/workspace.json")
    if not os.path.exists(path):
        return None
    with open(path, "r", encoding = "utf-8") as f:
        config = json.load(f)
    return Workspace(config)


def _set_workspace(directory):
    workspace = get_workspace() or Workspace({})
    workspace.path = directory
    path = os.path.expanduser("~/.cpt/workspace.json")
    with open(path, "w", encoding = "utf-8") as f:
        json.dump(workspace.to_dict(), f)


def set_workspace(args):
    path = args.target_dir or "."
    if args.use_workspace:
        cur_workspace = get_workspace()
        if cur_workspace is None:
            print("No workspace assigned. Please disable the -w/--workspace argument or assign a workspace with `cpt workspace`.")
            exit(0)
        path = os.path.join(cur_workspace.path, path)
    path = os.path.abspath(path)
    _set_workspace(path)


def disable_workspace(args):
    path = os.path.expanduser("~/.cpt/workspace.json")
    if os.path.exists(path):
        os.remove(path)
