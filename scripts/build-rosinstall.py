import sys
import os
import argparse
import logging
import subprocess

import docker
import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DOCKER_IMAGE_TIME_MACHINE = 'robust-rosin/rosinstall_generator_time_machine:02'

DIR_HERE = os.path.dirname(__file__)
# DIR_TIME_MACHINE = os.path.abspath(os.path.join(DIR_HERE, 'time_machine'))

DESCRIPTION = "build-rosinstall"


def find_bug_descriptions(d):
    buff = []
    for root, _, files in os.walk(d):
        for fn in files:
            if fn.endswith('.bug'):
                fn = os.path.join(root, fn)
                buff.append(fn)
    return buff


def build_file(fn_bug_desc, overwrite=False):
    logger.info("building rosinstall file for file: %s", fn_bug_desc)
    bug_id = os.path.basename(fn_bug_desc)[:-4]
    dir_bug = os.path.dirname(fn_bug_desc)
    fn_rosinstall = os.path.join(dir_bug, 'deps.rosinstall')

    # check for existence of Docker image for time machine
    client_docker = docker.from_env()
    try:
        client_docker.images.get(DOCKER_IMAGE_TIME_MACHINE)
    except docker.errors.ImageNotFound:
        logger.warning("Docker image for time machine not found: %s",
                       DOCKER_IMAGE_TIME_MACHINE)
        sys.exit(1)

    if os.path.isfile(fn_rosinstall):
        if overwrite:
            logger.warning("overwriting file: %s", fn_rosinstall)
        else:
            logger.info("skipping existing file: %s", fn_rosinstall)
            return

    with open(fn_bug_desc, 'r') as f:
        d = yaml.load(f)

    if 'issue' in d['time-machine']:
        issue_or_datetime = d['time-machine']['issue']
    elif 'datetime' in d['time-machine']:
        issue_or_datetime = d['time-machine']['datetime'].isoformat()
    else:
        raise Exception("expected 'issue' or 'datetime' in 'time-machine'")

    ros_pkgs = d['time-machine']['ros_pkgs']
    if len(ros_pkgs) > 1:
        raise Exception("the time machine doesn't currently support more than ROS package")

    cmd = [
        'rosinstall_generator_tm.sh',
        issue_or_datetime,
        bug_id,
        d['time-machine']['ros_distro'],
        ros_pkgs[0],
        os.path.abspath(fn_rosinstall),
    ]
    logger.debug("executing command: %s", ' '.join(cmd))
    subprocess.check_call(cmd, cwd=DIR_HERE)


def build_dir(d, overwrite=False):
    logger.info("building rosinstall files for directory: %s", d)
    files = find_bug_descriptions(d)
    for fn in files:
        try:
            build_file(fn, overwrite=overwrite)
        except Exception:
            logger.exception("failed to create rosinstall file for bug: %s", fn)


def main():
    log_to_stdout = logging.StreamHandler()
    log_to_stdout.setLevel(logging.DEBUG)
    logger.addHandler(log_to_stdout)

    parser = argparse.ArgumentParser(description=DESCRIPTION)
    parser.add_argument('file_or_dir', type=str)
    parser.add_argument('--overwrite', action='store_true')
    args = parser.parse_args()
    fn_or_dir = args.file_or_dir

    if os.path.isdir(fn_or_dir):
        build_dir(fn_or_dir, overwrite=args.overwrite)
    elif os.path.isfile(fn_or_dir):
        build_file(fn_or_dir, overwrite=args.overwrite)
    else:
        logger.error("ERROR: expected a filename or directory.")
        sys.exit(1)


if __name__ == '__main__':
    main()
