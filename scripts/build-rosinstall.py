import sys
import os
import argparse
import logging
import subprocess

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DESCRIPTION = "build-rosinstall"


def find_bug_descriptions(d):
    buff = []
    for root, _, files in os.walk(d):
        for fn in files:
            if fn.endswith('.bug'):
                fn = os.path.join(root, fn)
                buff.append(fn)
    return buff


def build_file(fn_bug_desc):
    logger.info("building rosinstall file for file: %s", fn_bug_desc)


def build_dir(d):
    logger.info("building rosinstall files for directory: %s", d)
    files = find_bug_descriptions(d)
    for fn in files:
        build_file(fn)


def main():
    log_to_stdout = logging.StreamHandler()
    log_to_stdout.setLevel(logging.INFO)
    logger.addHandler(log_to_stdout)

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('file_or_dir', type=str)
    args = parser.parse_args()
    fn_or_dir = args.file_or_dir

    if os.path.isdir(fn_or_dir):
        build_dir(fn_or_dir)
    elif os.path.isfile(fn_or_dir):
        build_file(fn_or_dir)
    else:
        logger.error("ERROR: expected a filename or directory.")
        sys.exit(1)


if __name__ == '__main__':
    main()
