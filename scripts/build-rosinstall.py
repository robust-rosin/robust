import sys
import os
import argparse
import logging
import subprocess
import shutil

import docker
import yaml
import requests

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DOCKER_IMAGE_TIME_MACHINE = 'robust-rosin/rosinstall_generator_time_machine:02'
BIN_TIME_MACHINE = 'rosinstall_generator_tm.sh'

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

    if not shutil.which(BIN_TIME_MACHINE):
        logger.warning("could not find time machine binary in PATH: %s",
                       BIN_TIME_MACHINE)
        sys.exit(1)

    if os.path.isfile(fn_rosinstall):
        if overwrite:
            logger.warning("overwriting file: %s", fn_rosinstall)
        else:
            logger.info("skipping existing file: %s", fn_rosinstall)
            return

    with open(fn_bug_desc, 'r') as f:
        d = yaml.load(f)

    # FIXME determine datetime from issue
    if 'issue' in d['time-machine']:
        issue = d['time-machine']
        raise Exception("'issue' is currently not supported.")

    if 'datetime' in d['time-machine']:
        dt = d['time-machine']['datetime'].isoformat()
    else:
        raise Exception("expected 'issue' or 'datetime' in 'time-machine'")

    ros_pkgs = d['time-machine']['ros_pkgs']
    if len(ros_pkgs) > 1:
        raise Exception("the time machine doesn't currently support more than ROS package")

    os.path.abspath(fn_rosinstall)

    cmd = [BIN_TIME_MACHINE, dt, d['time-machine']['ros_distro']]
    cmd += ros_pkgs
    cmd += ['--deps', '--tar']
    logger.debug("executing command: %s", ' '.join(cmd))

    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        contents, stderr = tuple(o.decode('utf-8') for o in p.communicate())
        if p.returncode != 0:
            logger.warning("time machine failed for bug [%s]:\n%s",
                           fn_bug_desc, stderr)
            return
    finally:
        p.kill()

    # updated repository names
    contents = contents.replace('geometry_experimental', 'geometry2')

    # write to rosinstall file
    with open(fn_rosinstall, 'w') as f:
        f.write(contents)


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
