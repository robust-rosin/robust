import os
import sys
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
        dir_bug = os.path.dirname(fn)
        fn_short = os.path.relpath(fn, DIR_ROBUST)
        logger.info("generating manifest for bug file [%s]", fn_short)

        def report_error(m):
            m = "bad bug file [{}]: {}".format(fn_short, m)
            warnings.warn(m)

        with open(fn, 'r') as f:
            desc = yaml.safe_load(f)
        try:
            bug_id = desc['id']
            ros_distro = desc['time-machine']['ros_distro']
            ros_pkgs = desc['time-machine']['ros_pkgs']
            is_build_failure = desc['bugzoo']['is-build-failure']
            sha_bug = desc['bugzoo']['bug-commit']
            sha_fix = desc['bugzoo']['fix-commit']
            url_forks = desc['bugzoo']['fork-urls']
        except KeyError as err:
            report_error('missing property [{}]'.format(err))
            continue

        fn_test = os.path.join(dir_bug, 'test.sh')
        if not os.path.isfile(fn_test):
            report_error('test.sh not found at {}'.format(fn_test))
            continue

        fn_deps = os.path.join(dir_bug, 'deps.rosinstall')
        if not os.path.isfile(fn_deps):
            report_error('deps.rosinstall not found at {}'.format(fn_deps))
            continue

        if not isinstance(is_build_failure, bool):
            report_error("'is_build_failure' should be a boolean")
            continue

        if not isinstance(url_forks, list):
            report_error("'bugzoo.url-forks' should be a list")
            continue

        if len(url_forks) > 1:
            report_error("BugZoo file does not support multiple forks.")
            continue

        # determine Ubuntu version based on ROS distro
        ubuntu_version = ({
            'kinetic': 'xenial-20180808',
            'jade': '15.04',
            'indigo': '14.04.5',
            'hydro': '12.04.5',
            'groovy': '12.04.5',
        }).get(ros_distro, '12.04.5')
        use_apt_old_releases = \
            ubuntu_version in ['15.04', '12.04.5']

        use_osrf_repos = desc['bugzoo'].get('use-osrf', False)
        if not isinstance(use_osrf_repos, bool):
            report_error("'use-osrf' should be a boolean")
            continue

        build_args = {
            'IS_BUILD_FAILURE': "yes" if is_build_failure else "no",
            'USE_APT_OLD_RELEASES': use_apt_old_releases,
            'USE_OSRF_REPOS': use_osrf_repos,
            'UBUNTU_VERSION': ubuntu_version,
            'ROS_DISTRO': ros_distro,
            'CATKIN_PACKAGES': ' '.join(ros_pkgs),
            'REPO_FORK_URL': url_forks[0],  # FIXME
            'REPO_BUG_COMMIT': sha_bug,
            'REPO_FIX_COMMIT': sha_fix
        }

        # create a separate blueprint for the buggy and fixed version
        # create a separate description for the buggy and fixed version
        for stage in ('bug', 'fix'):
            name_image = 'robustrosin/robust:{}-{}'.format(bug_id, stage)
            blueprints.append({'file': 'Dockerfile',
                               'tag': name_image,
                               'build-stage': stage,
                               'context': os.path.relpath(dir_bug, DIR_ROBUST),
                               'arguments': build_args})
            bugs.append({'name': 'robust:{}:{}'.format(bug_id, stage),
                         'image': name_image,
                         'dataset': 'robust',
                         'languages': ['cpp'],  # FIXME
                         'source-location': '/ros_ws/src',
                         'test-harness': {'type': 'empty'},
                         'compiler': {'type': 'catkin',
                                      'workspace': '/ros_ws/src',
                                      'time-limit': 300}})

    # create YAML
    yml = {'version': '1.0',
           'blueprints': blueprints,
           'bugs': bugs}
    fn_bugzoo = os.path.join(DIR_ROBUST, 'robust.bugzoo.yml')
    with open(fn_bugzoo, 'w') as f:
        yaml.dump(yml, f, default_flow_style=False)


if __name__ == '__main__':
    main()
