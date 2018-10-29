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

"""
def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('-t', '--time', dest='start_time')
    return parser.parse_args(args)
"""
