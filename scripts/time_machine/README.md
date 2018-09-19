# rosinstall_generator_time_machine

A simple bash script to generate `.rosinstall` files 'from the past'.


## Overview

This is a bash script that will, given a GitHub issue link, a date in the past and some other bits of information, try to generate a `.rosinstall` file using `rosinstall_generator` and a clone of `ros/rosdistro` as it was at the date specified.

The `.rosinstall` file can then be used to build the set of ROS packages that will approximate the 'state of ROS' as it was at the time the issue was reported.

## Usage

```
rosinstall_generator_tm.sh [ ISSUE_URL | ISO8601_DATETIME ] BUG_ID ROS_DISTRO PUT ROSINSTALL_FILENAME
```

Example invocation to generate a `.rosinstall` file, based on an issue opened on the `yujinrobot/kobuki_core` tracker on the 1st of March 2017 (note reuse of the cache):

```shell
user@machine:~$ rosinstall_generator_tm.sh \
  https://github.com/yujinrobot/kobuki_core/issues/29 \
  eed104d \
  kinetic \
  kobuki_ftdi \
  deps_eed104d.rosinstall
Switched to branch 'master'
Your branch is up-to-date with 'origin/master'.
Retrieving issue 'created_at' property for: https://github.com/yujinrobot/kobuki_core/issues/29
Found: 2017-03-01T08:57:20Z
Determined rosdistro commit: 2af311e205b874e862be155ffe21cb54e902f60b
Reusing existing branch
Switched to branch 'bughunt_eed104d'
Skipping rosdistro cache, already exists
Creating temporary rosdistro index ..
Using temporary index to generate rosinstall file (dependencies only) ..
Using ROS_DISTRO: kinetic
Storing metadata ..
Done
```

The same invocation, but with a datetime instead of an issue url:

```shell
user@machine:~$ rosinstall_generator_tm.sh \
  2017-03-01T08:57:20Z \
  eed104d \
  kinetic \
  kobuki_ftdi \
  deps_eed104d.rosinstall
...
```

**Note**: be prepared to press <kbd>RET</kbd> a few times for some repositories that no longer exist, or are now private repositories (and for which `git` would now need a password).

This will generate the `deps_eed104d.rosinstall` file containing all dependencies (and only the dependencies) of the `kobuki_ftdi` package in ROS Kinetic at the time that `yujinrobot/kobuki_core/issues/29` was reported. It will also generate a yaml file containing some metadata (`ros/rosdistro` commit used, issue created stamp, ROS distribution, etc) and a directory containing the `rosdistro` cache that was used to generate the `.rosinstall` file.


## Requirements

In order to be able to run this, the following need to be present:

 - git
 - Python 2
 - `rosdistro` Python library ([this fork](https://github.com/rosin-project/rosdistro_python/tree/rosin_bughunt_0.6.8), `rosin_bughunt_0.6.8` branch)
 - `rosinstall_generator`
 - PyGitHub

It is recommended to install these dependencies (ie: `rosdistro` and `rosinstall_generator`) in a Python virtual environment (order matters):

```shell
virtualenv ritm_venv
source ritm_venv/bin/activate
pip install -U pip
pip install wheel
pip install git+https://github.com/rosin-project/rosdistro_python@rosin_bughunt_0.6.8
pip install rosinstall_generator
pip install PyGitHub
```

At this point the environment setup should be complete and the tool can be used. Do not forget to (re)activate the virtual environment again when needed.


## Limitations

The current implementation can only go back to 25th of January, 2014 (on that date updates to various packages including `rosdistro` and `rosinstall_generator` was rolled out for REP-141 compliance).
It also cannot reuse any caches that are 'close' or 'near' in time to a previous cache right now, leading to the tool always (re)building a rosdistro cache, even if there is only a minor time difference between two subsequent `rosdistro` commits.

It (obviously) cannot provide information on repositories that no longer exist (this becomes more of a problem the further back in time one goes).


## Future work

 - probably rewrite in Python
 - extend support to `version 2` and earlier versions of `rosdistro` (and related tools)
 - add reuse of existing caches that are 'near in time'
 - host caches in an online repository to avoid having to build them in the first place
 - silence `rosdistro_build_cache` a bit
 - expand metadata generation to include more details
 - distribute this tool in a Docker image
 - integrate with OSRF [Legacy ROS](https://hub.docker.com/r/osrf/ros_legacy/tags/) Docker images

## FAQ

Some frequently asked questions and answers.

#### Date YYYY-MM-DDTHH:MM:SS too far in the past

This error is printed whenever the script is asked to go back to a date that is beyond what is currently supported (25th of January 2014).

#### No packages/stacks left after ignoring not released

After figuring out the `rosdistro` commit, the script uses `rosinstall_generator` to generate a `.rosinstall` file with all the dependencies of the specified PUT. For this to work, the PUT itself must have been released (and thus registered in `rosdistro`) at the date and time that the time machine was asked to go back to.

Make sure this is the case if running into this error. Realise that the package may not have been released at the time the bug was reported (if using the issue URL as input to the time machine).
