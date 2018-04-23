# ROBUST

## Installation

```
$ pip3 install --user bugzoo
```

The ROBUST dataset can be added to BugZoo as either a remote source:

```
$ bugzoo source add robust https://github.com/robust-rosin/robust
```

or as a local source

```
$ cd path/to/robust-rosin
$ bugzoo source add robust .
```

### Bug Installation

Now that you've added ROBUST as a source to your BugZoo installation, you can
begin building containers for each of the bugs inside the ROBUST dataset by
using the `bugzoo bug build` command, as shown below:

```
$ bugzoo bug build --force robust:ca23e58
```

where `ca23e58` is replaced by the identifier (i.e., the SHA-8) of the bug that
you wish to build. The `--force` option instructs BugZoo to attempt to rebuild
the image even if it is already installed -- don't worry, thanks to Docker's
caching mechanism, rebuilding takes a few seconds at most (if there have been
no changes to the image).

To determine the current replication status of a particular bug, refer to the
[progress tracker](https://github.com/robust-rosin/robust/blob/master/doc/progress.csv).

## Interacting with the bugs

To launch an interactive container for one of the bugs, execute the following:

```
$ bugzoo container launch robust:b4dc23c
```

where the `robust:b4dc23c` is replaced by the name of the bug.

The `bugzoo container execute` command can be used to perform headless
interaction with the bugs. For instance, in the example below, the developer
fix is applied to the source code, the package under test is rebuilt, and the
test is executed.

```
$ bugzoo container execute robust:b4dc23c ./fix && ./build.sh && ./test.sh
```

## Container Anatomy

Each container provided by this repository contains the following files, all of
which are located at `/ros_ws`:

* `build.sh`: is used to (re-)compile the package under test (PUT).
  `build.sh` should exit with code `0` if the PUT was successfully built.
  Conversely if the PUT fails to build, `build.sh` may exit with any code other
  than `0`.
* `test.sh`: provides a test script that tests for the presence or absence of
  the bug. For build-related bugs, `test.sh` simply calls `build.sh`. If the
  test passes and the bug is not detected, `test.sh` should produce an exit
  code `0`. Failing the test may cause `test.sh` to return any exit code other
  than `0`. The same behaviour should also apply to build-related issues; that
  is, `test.sh` should exit with `0` if the build was successful, and any other
  exit code if not.
* `fix`: switches the source code for the PUT to its buggy state.
* `unfix`: switches the source code for the PUT to its fixed state.
* `fix.patch`: provides the developer patch that was used to fix the bug.

Note that `build.sh`, `fix.patch`, `fix`, and `unfix` are automatically
generated during the BugZoo build process. `test.sh` and any files related to
testing are hosted by the directory for each scenario.
