Creating a BugZoo snapshot
--------------------------

In this document, we provide instructions for creating a BugZoo snapshot for
a particular bug within this dataset. Note that these instructions are
intended for the maintainers of the ROBUST dataset, and not for end-users of
ROBUST.

## Instructions

1.  Identify the package to which the bug belongs (e.g., `kobuki`), then create
    a subdirectory to hold all files for the bug within the directory for that
    package (e.g., `kobuki/eed104d`). For the remainder of these instructions,
    the newly created directory for the bug will be referred to as the
    *bug directory*.
2.  For the sake of better organisation, move the `.bug` file for the bug into
    the bug directory.
3.  Use the [ROS install time machine](https://github.com/rosin-project/rosinstall_generator_time_machine)
    to generate a `.rosinstall` file for the non-fixed version of your bug.
    The `.rosintall` file is responsible for specifying all of the dependencies
    (together with fixed versions) of the package under test (PUT).
    The generated `.rosinstall` file should be saved to `deps.rosinstall`
    inside the bug directory.
4.  Next, we need to create a separate branch for the buggy and fixed versions
    of the code within the forked repository for the package under test. Each
    branch is responsible for providing any additional files that are required
    to reproduce the bug (i.e., test cases). The buggy and fixed branches
    should be named `${SHA8}_robust_buggy` and `${SHA8}_robust_fixed`,
    respectively, where `${SHA8}` is replaced by the name (i.e., the short SHA)
    of the bug. To generate these branches, you should checkout the buggy or
    fixed version of the PUT using the information provided by the `.bug` file,
    and branch from those points. After you've created the branches, don't
    worry about creating any additional files (e.g., test cases) -- those can
    come later.
5.  Finally, create a file named `manifest.bugzoo.yml` inside the bug
    directory. This file is going to be responsible for providing BugZoo with
    all of the necessary information for building and interacting with the bug.
    Below is a template for the contents of the file:
    ```yaml
    version: '1.0'

    blueprints:
      - type: docker
        tag: robustrosin/robust:__NAME__
        file: ../../Dockerfile
        arguments:
          IS_BUILD_FAILURE: __IS_BUILD_FAILURE__
          USE_APT_OLD_RELEASES: __USE_APT_OLD_RELEASES__
          UBUNTU_VERSION: __UBUNTU_VERSION__
          ROS_DISTRO: __ROS_DISTRO__
          CATKIN_PKG: __PUT__
          REPO_FORK_URL: __FORK_URL__
          REPO_BUG_COMMIT: __BUG_COMMIT__
          REPO_FIX_COMMIT: __FIX_COMMIT__

    bugs:
      - name: robust:__NAME__
        image: robustrosin/robust:__NAME__
        program: __PUT_NAME__
        dataset: robust
        languages:
          - cpp
        source-location: /ros_ws/src
        test-harness:
          type: empty
        compiler:
          type: catkin
          workspace: /ros_ws/src
        time-limit: 300
    ```
    The `blueprints` section of the file is responsible for providing BugZoo
    with instructions for building the Docker image for the bug. To prepare
    this section for your bug, you should take the following steps:
    * All instances of `__NAME__` should be replaced by the short name of the
      bug (e.g., `eed104d`).
    * `__BUG_COMMIT__` and `__FIX_COMMIT__` should be replaced with the SHA
      hashes for the head of the buggy and fixed branches for the PUT. Note
      that if any commits are pushed to either of the branches, the
      `__BUG_COMMIT__` and `__FIX_COMMIT__` will need to be updated. This step
      is necessary to prevent Docker's build caching from ignoring updates to
      the branches.
    * `__FORK_URL__` should be replaced with the URL of the forked repository
      for the PUT (e.g., `https://github.com/robust-rosin/ros_comm`).
    * `__IS_BUILD_FAILURE__` should be set to `"yes"` if the bug
      is a build failure, or `"no"` if it is not. **The value of this argument
      MUST be enclosed in quotes to avoid it being incorrectly parsed.**
    * `__USE_APT_OLD_RELEASES__` should be set to `"yes"` if the version of
      Ubuntu is no longer maintained. If the version of Ubuntu is still being
      supported, then `"no"` should be used instead.
      **Once again, the value of this argument MUST be enclosed in quotes to
      avoid it being incorrectly parsed.**
