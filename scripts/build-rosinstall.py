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

DIR_HERE = os.path.dirname(__file__)
DOCKER_IMAGE_TIME_MACHINE = 'robust-rosin/rosinstall_generator_time_machine:03'
BIN_TIME_MACHINE = 'rosinstall_generator_tm.sh'

DESCRIPTION = "build-rosinstall"


def find_bug_descriptions(d):
    buff = []
    for root, _, files in os.walk(d):
        for fn in files:
            if fn.endswith('.bug'):
                fn = os.path.join(root, fn)
                buff.append(fn)
    return buff


def gh_issue_to_datetime(url_issue):
    # type: (str) -> str
    prefix = "https://github.com/"
    owner, repo, _, number = url_issue[len(prefix):].split('/')
    url_api = 'https://api.github.com/repos/{}/{}/issues/{}'
    url_api = url_api.format(owner, repo, number)
    r = requests.get(url_api)
    created_at = r.json()['created_at']
    return created_at


def _time_machine(packages,
                  dt,
                  distro,
                  deps_only=True):
    # type: (List[str], str, str) -> Dict[str, Dict[str, str]]
    cmd = [BIN_TIME_MACHINE, dt, distro] + packages
    cmd += ['--deps', '--tar']
    if deps_only:
        cmd += ['--deps-only']
    logger.debug("executing command: %s", ' '.join(cmd))

    try:
        res = subprocess.run(cmd,
                             check=True,
                             stdout=subprocess.PIPE)
        contents = res.stdout.decode('utf-8')
    except subprocess.CalledProcessError as err:
        logger.warning("time machine failed (return code: %d)",
                       err.returncode)
        return

    return {e['tar']['local-name']: e['tar'] for e in yaml.load(contents)}


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

    distro = d['time-machine']['ros_distro']
    ros_pkgs = d['time-machine']['ros_pkgs']
    missing_deps = d['time-machine'].get('missing-dependencies', [])

    if 'datetime' in d['time-machine']:
        dt = d['time-machine']['datetime'].isoformat()
        if dt[-1] != 'Z':
            dt += 'Z'
    elif 'issue' in d['time-machine']:
        url_issue = d['time-machine']['issue']
        try:
            dt = gh_issue_to_datetime(url_issue)
        except Exception:
            m = "failed to convert GitHub issue to ISO 8601 timestamp: {}"
            m = m.format(url_issue)
            raise Exception(m)
    else:
        raise Exception("expected 'issue' or 'datetime' in 'time-machine'")

    try:
        deps = {}
        deps.update(_time_machine(ros_pkgs, dt, distro, deps_only=True))
        if missing_deps:
            deps.update(_time_machine(missing_deps, dt, distro, deps_only=False))
    except subprocess.CalledProcessError as err:
        logger.warning("time machine failed (return code: %d) for bug [%s]",
                       err.returncode, fn_bug_desc)
        return

    # added to the top of the file after processing
    header = ''

    # ensure catkin >= 0.5.78 (i.e., supports --only-pkg-with-deps)
    # https://github.com/ros/catkin/commit/913488427d2ff18b808764d1eaf38acead67e18f
    if not 'catkin' in deps:
        raise Exception("expected 'catkin' package in .rosinstall file")
    version_str_catkin = deps['catkin']['version'].split('-')[-2]
    version_catkin = tuple(map(int, version_str_catkin.split('.')))
    if version_catkin <= (0, 5, 78):
        msg = "updated 'catkin' version ({}) to 0.5.78 to support --only-pkg-with-deps".format(version_str_catkin)
        header += "# build-rosinstall.py: {}\n".format(msg)
        logger.warning(msg)

    contents = yaml.dump([{'tar': e} for e in deps.values()],
                         default_flow_style=False)

    # updated repository names
    if 'geometry_experimental' in contents:
        msg = "updated 'geometry_experimental' URLs to refer to the 'geometry2' repository (it was renamed in https://github.com/ros/geometry2/issues/160)"
        header += '# build-rosinstall.py: {}\n'.format(msg)
        logger.warning(msg)
        contents = contents.replace('geometry_experimental', 'geometry2')

    # prepend header
    contents = header + contents

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
