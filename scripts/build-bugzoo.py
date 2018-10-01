import os
import logging
import warnings

import yaml

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DIR_HERE = os.path.dirname(__file__)
DIR_ROBUST = os.path.abspath(os.path.join(DIR_HERE, '..'))


def find_bug_descriptions(d):
    buff = []
    for root, _, files in os.walk(d):
        for fn in files:
            if fn.endswith('.bug'):
                fn = os.path.join(root, fn)
                buff.append(fn)
    return buff


def main():
    log_to_stdout = logging.StreamHandler()
    log_to_stdout.setLevel(logging.DEBUG)
    logger.addHandler(log_to_stdout)

    blueprints = []
    bugs = []
    files = find_bug_descriptions(DIR_ROBUST)
    for fn in files:
        with open(fn, 'r') as f:
            desc = yaml.load(f)

        bug_id = os.path.basename(fn)[:-4]
        package = os.path.basename(os.path.dirname(fn))
        ros_distro = desc['time-machine']['ros_distro']
        ros_pkgs = desc['time-machine']['ros_pkgs']
        if len(ros_pkgs) > 1:
            warnings.warn('BugZoo file does not currently support multiple PUTs')
            continue
        catkin_pkg = ros_pkgs[0]

        try:
            is_build_failure = desc['bugzoo']['is_build_failure']
        except KeyError:
            msg = 'bug file [%s] is missing "bugzoo.is_build_failure"'
            msg = msg.format(bug_id)
            warnings.warn(msg)
            continue

        # determine fork URL
        if 'bugzoo' in desc and 'fork-url' in desc['bugzoo']:
            url_fork = desc['bugzoo']['fork-url']
        else:
            url_fork = ({
                'kobuki': 'https://github.com/robust-rosin/kobuki',
                'geometry2': 'https://github.com/robust-rosin/geometry2',
                'universal_robot': 'https://github.com/robust-rosin/universal_robot',
                'ros_comm': 'https://github.com/robust-rosin/ros_comm',
                'mavros': 'https://github.com/robust-rosin/mavros'
            })[package]

        # determine commit SHA1s
        try:
            sha_bug = desc['bugzoo']['bug-commit']
            sha_fix = desc['bugzoo']['fix-commit']
        except KeyError as err:
            msg = "bug file [%s] is missing '%s'"
            msg = msg.format(bug_id, err)
            warnings.warn(msg)
            continue

        # determine Ubuntu version based on ROS distro
        ubuntu_version = ({
            'kinetic': '16.04',
            'jade': '15.04',
            'indigo': '14.04',
            'hydro': '12.04',
            'groovy': '12.04',
        }).get(ros_distro, '12.04')
        use_apt_old_releases = \
            ubuntu_version in ['15.04', '12.04']

        build_args = {
            'IS_BUILD_FAILURE': is_build_failure,
            'USE_APT_OLD_RELEASES': use_apt_old_releases,
            'UBUNTU_VERSION': ubuntu_version,
            'ROS_DISTRO': ros_distro,
            'CATKIN_PKG': catkin_pkg,
            'REPO_FORK_URL': url_fork,
            'REPO_BUG_COMMIT': sha_bug,
            'REPO_FIX_COMMIT': sha_fix
        }

        name_image = 'robustrosin/robust:{}'.format(bug_id)
        blueprints.append({
            'tag': name_image,
            'file': '{}/Dockerfile'.format(package),
            'context': '{}/{}'.format(package, bug_id),
            'arguments': build_args
        })
        bugs.append({
            'name': 'robust:{}'.format(bug_id),
            'image': name_image,
            'program': package,
            'dataset': 'robust',
            'languages': ['cpp'],  # FIXME
            'source-location': '/ros_ws/src',
            'test-harness': {'type': 'empty'},
            'compiler': {'type': 'catkin',
                         'workspace': '/ros_ws/src',
                         'time-limit': 300}
        })

    # create YAML
    yml = {'version': '1.0',
           'blueprints': blueprints,
           'bugs': bugs}
    fn_bugzoo = os.path.join(DIR_ROBUST, 'robust.bugzoo.yml')
    with open(fn_bugzoo, 'w') as f:
        yaml.dump(yml, f, default_flow_style=False)


if __name__ == '__main__':
    main()
