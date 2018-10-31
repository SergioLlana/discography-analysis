import argparse
import json


def read(path):
    try:
        with open(path, 'r') as f:
            return f.read()
    except IOError:
        return ""


def read_json(path):
    try:
        return json.loads(read(path))
    except Exception:
        return {}


def write_json(path, data_dict):
    try:
        with open(path, 'w') as f:
            json.dump(data_dict, f, indent=2)
    except Exception:
        pass
