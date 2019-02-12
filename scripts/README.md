# Additional Scripts

## Installation

Make sure to have a Python environment active with the required modules in it.

Use `pip install -r requirements.txt` in this (ie: the `scripts/`) directory to install them with `pip`.

Steps for a virtual environment with everything setup to use these scripts:

```
$ virtualenv --python=python3 $HOME/robust_venv
$ source $HOME/robust_venv/bin/activate
$ pip3 install -r requirements.txt
```

If you already have a virtual environment for use with BugZoo (see main [README](../README.md)) that could be used as well (just skip creation of a new virtual environment in the steps above).


## `build-rosinstall.py`

Used to conveniently generate a rosinstall file for the bug belonging to
a given `.bug` file, or to generate all of the `.rosinstall` files for
all `.bug` files belonging to a given directory.

```
$ python scripts/build-rosinstall.py mavros/08cd181.bug
$ python scripts/build-rosinstall.py .
```

An optional `--overwrite` flag can be passed to instruct the script to
overwrite any existing `.rosinstall` files. By default, if a `.rosinstall`
file already exists for a given bug, that file will be skipped.

**Note:** This script assumes that the `rosinstall_generator_time_machine`
  binary is visible from the `PATH`.

This script uses the `time-machine` section of a bug description file to
construct its corresponding `deps.rosinstall` file. The `time-machine`
section contains the following properties:

* `ros_distro`: specifies the distribution of ROS that should be used.
  Supported values: `kinetic`, `jade`, `indigo`, `hydro`, `groovy`,
  `fuerte`, `electric`.
* `ros_pkgs`: a list of the names of the packages under test (PUTs).
* `missing-dependencies`: an optional list of the names of packages that are
  undeclared dependencies of the PUTs.
* `issue`: an optional link to issue where the bug is reported. The time
  machine uses this information to determine the point in time at which
  the bug was reported.
* `datetime`: if no `issue` is provided, `datetime` can be used to specify,
  using an ISO-8601 date-time string, the approximate time at which the
  bug was reported.

Below is an example of a `time-machine` section, taken from
`mavros/08cd181.bug`.

```yaml
time-machine:
  ros_distro: hydro
  ros_pkgs:
    - mavros
  issue: https://github.com/mavlink/mavros/issues/161
```

## `build-bugzoo.py`

Used to construct a single BugZoo manifest file that packages all of the bug
scenarios within ROBUST as BugZoo snapshots. This file takes no arguments; it
simply scans for all `.bug` files and uses their contents to build a BugZoo
manifest file which is saved to the root of the repository.

```
$ python build-bugzoo.py
```

To construct a BugZoo snapshot (and accompanying blueprint) definition for a
bug scenario within ROBUST, this script uses information provided by the
`bugzoo` and `time-machine` sections of the `.bug` file.
Below is an excerpt from `mavros/08cd181.bug`.

```yaml
time-machine:
  ros_distro: hydro
  ros_pkgs:
    - mavros
  issue: https://github.com/mavlink/mavros/issues/161
bugzoo:
  fork-urls: 
    - https://github.com/robust-rosin/mavros
  is-build-failure: yes
  use-osrf: no  # [optional]
  bug-commit: 665484a19c47771cc68200b2cd2c5c75a77995ac
  fix-commit: 08cd18164e729b0fb0ed1f6b553e5458eb9b6a4c
```

The script uses the `ros_distro` section of the `time-machine` section to
determine which version of ROS to use (along with a suitable version of Ubuntu
for that ROS version). The `ros_pkgs` property of the `time-machine` section is
also used to determine the appropriate fork for the PUTs. (At the time of
writing, the script only supports bugs that specify a single PUT.)

The `bugzoo` section contains the following properties:
* `is-build-failure`: whether the build is expected to fail for the PUT.
* `bug-commit` and `fix-commit`: give the commit hashes for the head of the bug witness and fix witness for the bug in
its fork. Note that these properties must be updated when the witness branches
are modified in order to break the cache and to ensure the image is up to date.
* `fork-urls`: lists the url(s) of the forked repository(/ies).
* `use-osrf` [optional]: whether or not BugZoo should use OSRF's sources when installing dependencies for the PUT. If `use-osrf` is not provided, its value will default to `no` (i.e., OSRF
sources will not be used).

**Note:** To use this script, `pyyaml` must be installed in the current
  environment.
