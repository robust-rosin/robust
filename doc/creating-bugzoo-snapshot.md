Creating a BugZoo snapshot
--------------------------

In this document, we provide instructions for creating a BugZoo snapshot for
a particular bug within this dataset. Note that these instructions are
intended for the maintainers of the ROBUST dataset, and not for end-users of
ROBUST.

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
    (together with fixed versions) of the program under test (PUT).
    The generated `.rosinstall` file should be saved to `deps.rosinstall`
    inside the bug directory.
