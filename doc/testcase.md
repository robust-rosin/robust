# Introduction

This file describes the procedure of reproduction of the bug in the ROBUST ROSIN repository. It is meant to be read by those who contribute to the repository.  Before reading this document, read about the general usage of the repository, anatomy and commands in [the top-level readme file](README.md). 

We explain the process using the bug b4dc23c as an example.  Go to [tf2/b4dc23c.L3/](tf2/b4dc23c.L3/) and run (requires a docker installation). This bug is now implemented so that you can test whether you have all the prerequistes set up by invoking:

```bugzoo bug build robust:b4dc23c```

This command should build robust:b4dc23c and all dependencies (so be patient).

Then you can run 

```bugzoo container launch robust:b4dc23c```

which opens the interactive shell inside the docker container, where you can try using your test cases.

TODO: so far the repositories are not cloned (Chris is working on this), so you need to clone your repo with the test and fix in there to experiment.


TODO: write how to execute the test, and how to execute the test with fix on our case study.

Now we are looking into how this is implemented. There are two major stages in the process: 

1. Preparation of the docker container with all the necessary source code.
2. Writing and deploying a test cases.

We describe both of these below.

# Preparation of the skeleton container #

This part is a bit sketchy &mdash; people doing this know the details well. It mostly describes what happens **before you start writing a test**. All the relevant files should be  should be in [tf2/b4dc23c.L3](tf2/b4dc23c.L3)). 

1. The [time machine](https://github.com/gavanderhoorn/rosin_bug_hunt_l3/issues/2) is used to produce the lists of dependent sources in the rosinstall format: 

  * [deps.rosinstall](tf2/b4dc23c.L3/deps.rosinstall): all sources of packages that the package under test depends on

  * [put.rosinstall](tf2/b4dc23c.L3/put.rosinstall): the source and commit which contains the bug 

  * [puts_with_deps.rosinstall](tf2/b4dc23c.L3/puts_with_deps.rosinstall): the concatanation of the previous two


2. The repository of the package containing the bug is forked under the [robust-rosin](https://github.com/robust-rosin/) organization, without renaming---if this has not been done before.  In this case we create [robust-rosin / geometry2](https://github.com/robust-rosin/geometry2).  The parent of the bug fixing commit is branched to ```bugname_robust_buggy``` and the fixed commit is branched to ```bugname_robust_fixed``` (in this case ```b4dc23c_robust_buggy``` and ```b4dc23c_robust_fixed``` respectively).

    To identify the parent commit of the fixing commit following the issue/pull-request link from the bug description and finding the right merge commit, then it will have a parent. For this example:

    ```
    git checkout a9dbba2e265458ab26a9c2ced03f604c51b95312
    git checkout -b b4dc23c_robust_buggy
    git tag b4dc23c_robust_buggy_released
    git push --tags
    ```

    The tag will have to be shifted after the tests are added (and released).  The commit **should be** (!) the same commit that was used to create the pkgs.rosinstall file. Otherwise you are likely to see build errors. Small deviations are probably ok.

    Also branch the fixing commit and tag appropriately. For our example:

    ```
    git checkout b4dc23c
    git checkout -b b4dc23c_robust_fixed
    git tag b4dc23c_robust_fixed_released
    git push --tags
    ``` 
    
    The tag will have to be shifted after the tests are added (and released)

3. `Dockerfile` is created following [roughly this procedure]( https://github.com/gavanderhoorn/rosin_bug_hunt_l3/issues/1). A single [Dockerfile](Dockerfile) is used for all the bugs now, and the bugzoo infrastructure builds the bug images. We are exploiting the parameters in Dockerfiles (a relatively new feature).

4. The bug specification for bugzoo is stored in a YAML file, one per system. The format is determined by the bugzoo project. Since b4dc23c is a geometry2 bug it is stored in [geometry2.bugzoo.yml](tf2/geometry2.bugzoo.yml).

5. `test.sh`: A script that builds the tests with catkin_make_isolated and then calls rostest with roughly this contents:

    ```bash
    /ros_ws/src/catkin/bin/catkin_make_isolated --pkg tf2_ros --make-args tests
    rostest tf2_ros bug_witness.test
    ```
   
    I suggest that `bug_witness.test` is a fixed name for our test launch file.  So only tf2_ros (the name of the offending package) is variable in that script. As you can see in `b4dc23c/test.sh` this file may need to be customized for the purpose of some tests (I need to make a script executable here). So you will likely be changing the generic file produced by @ChrisTimperley.

6. `fix.sh`: A completely generic script, the same for all the bugs, that switches the PUT checkout from the tag `robust_buggy_released` to `robust_fixed_released`, so that you can run the test on the fixed code.

7. `unfix.sh`: A completely generic script, the same for all the bugs, that switches the PUT checkout from the tag `robust_fixed_released` to the tag `robust_buggy_released`, so that you can run the test on the buggy code.

8. `build.sh`: A script for initiating the build of the workspace.

# Writing and deploying the test-case #

After getting a complete L3 directory with the above files  from Chris, identify the repo and the issue (or pull request) number of the bug. 

1. git-clone the bug development repo locally and move to the buggy branch where we will be developing the test

    ```bash
    git clone b4dc23c_geometry2
    git checkout robust_buggy
    ```

2. Develop the test, committing any required changes to this branch. 
	
    a. We want the test to fail before applying fix, pass after applying the fix (this is hard for ``b4dc23c`` and possible for many others) and capture the problem as precisely as possible.
	
    b. You likely need a test launch file: Create it in **tf2_ros/test/bug_witness.test** (of course choosing your package name for tf2_ros). Then the scripts using rostest (above) will be able to pick up this file.
	
    c. Try to write the test to be as non-invasive as possible: as separate unit tests for functions, or as separate test nodes.  The changes to the original files should be minimal (as otherwise we are spoiling their realism).  Ideally we don't want to modify historical files at all; This is possible if the property is testable through a unit test or a node test.  If we have to do it, we keep our modifications as far as possible outside (for instance in a header file). Any new added code is in external files.  
	
    d. Standard file names for our added code are: **test/bug_witness.cpp** or **test/bug_witness.py** (the header goes to **include/package_name/bug_witness.h**). This will help any code transformation tools using the benchmark later to distinguish the testing code from the actual code. 



3. You can commit to the branch while you are working, as usual. You need to move the code to the container to test whether the test case actually fails.  Start the container, switch the directory to the repo, pull, and checkout the right branch. This is an example (of coruse your sessions will vary wildly):

    ```bash
    bugzoo container launch robust:b4dc23c
    cd src/b4dc23c_geometry2/
    git pull
    git checkout robust_buggy
    cd ../../
    ./test.sh
    ```

    You can, of course, continue the development of the test inside the container, but likely you will find the environment lacking.  So it is probably easier to stay outside and push the code via github.
    
    
4. As you have seen above, you invoke the test with ``./test.sh``. You need to  modify this file in order to call the right test (with the right parameters, etc). The fie is in the bug directory in the ``robust`` repo.  To have this file inside the container you will need to rebuild the container after every change - this should be fast at this stage.

5. You also need to test whether the test passes on the container containing the fix code:

    ```bash
    $ bugzoo container launch robust:b4dc23c
    $ cd src/b4dc23c_geometry2/
    $ git pull
    $ git checkout robust_fixed
    $ git merge robust_buggy
    $ cd ../../
    $ ./test.sh
    ```

    The test should pass if everything is alright. (Then you can also try to push the test files to the fixed branch, but you can also do it from the outside of the container).

6. Once the test case works both on the buggy and fixed branches, we need to release it.  I assume that your local checkout of b4dc23c_geometry2 (outside the container) has all the test code on both branches now.  We just need to move the release tags. This commands are to be invoked inside the b4dc23c_geometry2 repo checkout, fully upto-date with upstream (if you pushed any changes from the container) and with no uncommitted changes (if you were doing development):

    ```bash
    $ git checkout robust_buggy
    $ git tag -d robust_buggy_released
    $ git push --tags
    $ git tag robust_buggy_released
    $ git push --tags

    $ git checkout robust_fixed
    $ git tag -d robust_fixed_released
    $ git push --tags
    $ git tag robust_buggy_fixed
    $ git push --tags
    ```

7. Now if everythin is fine you should be able to do:

    ```bash
    # run the container
    $ bugzoo container launch robust:b4dc23c
    # compile the workspace
    $ ./build.sh
    # see the test fail
    $ ./test.sh
    # apply the fixing commit (not yet implemented)
    $ ./fix.sh
    # build the corrected code
    $ ./build.sh
    # see the test passing
    $ ./test.sh
    ```

    The same should be possible from outside

    ```bash
    bugzoo container execute robust:b4dc23c ./build.sh && ./test.sh
    # test fails after this execution
    bugzoo container execute robust:b4dc23c ./fix.sh && ./build.sh && ./test.sh
    # test passes after this execution
    ```

8. Revise the bug description to match the problem: now you really understand what the bug is, so please read the description file and fix any inaccuracies.  In the bug description file add the field "reproduction:" under the bug part, in which you can mention an important decisions you made in the reproduction process.  If you failed to reproduce, document why (also in the ``reproduction`` field in the bug description).

9. Consider creating the  L2 bug - now you really understand how to do this.
