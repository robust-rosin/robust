# Additional Scripts

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
