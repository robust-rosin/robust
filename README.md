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

```
$ bugzoo bug build robust:ca23e58
$ bugzoo bug build robust:b826eae
$ bugzoo bug build robust:eed104d
$ bugzoo bug build robust:b4dc23c
```

## Anatomy

* For bugs unrelated to the build process, `test.sh` is used to provide a test
  case that manifests the bug.
