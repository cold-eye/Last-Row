import argparse
import urllib


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default="local")
    args = parser.parse_args()

    return args


def parse_url(path):
    return urllib.parse.quote(path, safe=":/")
