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


2. The repository of the package containing the bug is forked under the [robust-rosin](https://github.com/robust-rosin/) organization, and named with the bug hash included as a prefix (robust/HASH_repo).  In this case we create [robust-rosin / b4dc23c_geometry2](https://github.com/robust-rosin/b4dc23c_geometry2).  The parent of the bug fixing commit is branched to ```robust_buggy``` and the fixed commit is branched to ```robust_fixed```.

3. **Dockerfile** is created following [roughly this procedure]( https://github.com/gavanderhoorn/rosin_bug_hunt_l3/issues/1). A single [Dockerfile](Dockerfile) is used for all the bugs now, and the bugzoo infrastructure builds the bug images. We are exploiting the parameters in Dockerfiles (a relatively new feature).

4. The bug specification for bugzoo is stored in a YAML file, one per system. The format is determined by the bugzoo project. Since b4dc23c is a geometry2 bug it is stored in [tf2.bugzoo.yml](tf2/tf2.bugzoo.yml).

5. **test.sh**: A script that builds the tests with catkin_make_isolated and then calls rostest with roughly this contents:

    ```/ros_ws/src/catkin/bin/catkin_make_isolated --pkg tf2_ros --make-args tests```

    ```rostest tf2_ros bug_witness.test```
   
    I suggest that bug_witness.test is a fixed name for our test launch file.  So only tf2_ros (the name of the offending package) is variable in that script. As you can see in ``b4dc23c/test.sh`` this file may need to be customized for the purpose of some tests (I need to make a script executable here). So you will likely be changing the generic file produced by @ChrisTimperley.

7. **fix.sh**: A completely generic script that applies fix.patch, so that you can test both before and after fixing.  @Chris: you are welcomed to think how we can avoid keeping completely generic files in every L3 bug, and how to make more files generic (reuse).

8. **test-with-fix.sh **A completely generic file that first calls fix.sh and then test.sh so that you can quickly use it as a singly command with docker run.

9. **entrypoint.sh: **A ros environment set up for the shell inside the container.  I have no idea if this could be somehow embedded inside the Dockerfile.

<!---
4. **fix.patch** a patch extracted from the fixing commit of ``b4dc23c`` using the following git command in the checkout of the repository with the buggy package (ideally already included by @ChrisTimperley):
``git format-patch -1 --src-prefix=a/geometry2/ --dst-prefix=b/geometry2/ b4dc23c54ba06a846c64215a2d8f944c5a1bd036 --stdout > path-to/b4dc23c/fix.patch``
   Note on the 'parameters': 
     * The hash is the hash of the fixing commit, from the ``b4dc23c.bug`` file (the bug description)
     * The path is to wherever the patch should land in the bug data repo
     * geometry2 (in two places) is the name of the repo that contains the bug (the directory name in the source space) - this simplifies the patch application later.
--->


# Writing and deploying the test-case #

After getting a complete L3 directory with the above files  from Chris, identify the repo and the issue (or pull request) number of the bug. 

1. (elided)

2. git-clone the new repo locally

3. Identify the parent commit of the fixing commit (the easiest by following the issue/pull-request and finding the right merge commit, then it will have a parent) and checkout this commit. For this example:

    ``git checkout a9dbba2e265458ab26a9c2ced03f604c51b95312``
    
    This **has to be** (!) the same commit as used by @gavanderhoorn to create the pkgs.rosinstall file. 

3. [outdated] Create a branch "bug_witness" from that commit in your local repo (later you obviously push it to the github remote as well):

    ``git checkout -b bug_witness``
    
     This will be useful for generating the patch as a difference between master and this branch.  

     For convenience we should also tag the start of this branch:

     ``git tag bug``

     ``git push --tags``

4. Create a file ``README.bug_witness`` at the root of this repo, containing a URL to your repo, plus any important comments about reproduction you think you need to make. This is so that we can find your repo if we wanted to fix something in this bug - this link will land in our patch file, so we can trace from the database to this repo.

     Of course you should commit to this repo, to the bug_witness branch as you go so that you have version control for your test development work.

6. Develop the test
	
      a. We want the test to fail before applying fix, pass after applying the fix (this is hard for ``b4dc23c`` and possible for many others) and capture the problem as precisely as possible.
	
      b. You likely need a test launch file: Create it in **tf2_ros/test/bug_witness.test** (of course choosing your package name for tf2_ros). Then the scripts using rostest (above) will be able to pick up this file.
	
      c. Try to write the test to be as non-invasive as possible: as separate unit tests for functions, or as separate test nodes.  The changes to the original files should be minimal (as otherwise we are spoiling their realism).  Ideally we don't want to modify historical files at all; This is possible if the property is testable through a unit test or a node test.  If we have to do it, we keep our modifications as far as possible outside (for instance in a header file). Any new added code is in external files.  
	
      d. Standard file names for our added code are: **test/bug_witness.cpp** or **test/bug_witness.py** (the header goes to **include/package_name/bug_witness.h**). This will help any code transformation tools using the benchmark later to distinguish the testing code from the actual code. 

7. Create a patch file **bug_witness.patch** and move it to the bug data repo.

    ``git diff --src-prefix a/geometry2/ --dst-prefix b/geometry2/ bug --cached > pathto/data/b4dc23c.L3/bug_witness.patch``

    We are referring to the origin commit of this branch with the tag "bug" created above.
In this case geometry2 (twice) is the name of the original repository (also the directory name that will be needed to generically apply the patch).  I couldn't find a simpler way to include it in the patch than with --src-prefix and --dst-prefix (improvements welcome!)

    It appears that ``git diff`` is oblivious to your local directory, as long as you are in the git tree, so this works from anywhere in the cloned code.

    The above method of creating a patch only works if you git-add all your changes, but you don't need to commit (which is convenient, because you would like to first test your patch in the docker container). So I usually do:

    ``git add -v &&`` ``git diff --src-prefix a/geometry2/ --dst-prefix b/geometry2/ bug --cached > ~/work/2017-42-bugs-in-ros/data/b4dc23c.L3/bug_witness.patch``

8. Build the the container. It should likely build nicely thanks to Gijs and Chris. Any bugs will be in your patch :)

    You just need to build the container: ``docker build -t b4dc23c .``  in the L3 directory. This already applies the test patch, and compiles the tests for you.

    In testing, you will occasionally find out that a clean build is needed, because otherwise you have stale files in the filesystem (not always Docker cleanly discovers that things should be rebuild):  ``docker build --no-cache -t b4dc23c .``  (This is a bit brutal, so if you have a quicker way, in your case, you may want to use it). I only needed this once in ``b4dc23c`` process.

9. Run the container

	* ``docker run -it b4dc23c`` (opens interactively, good for debugging)

	* compile and run tests with [./test.sh](file:///home/wasowski/Dropbox/Notes/20160318_ICT_26_ROSIN/42_bugs_in_ROS/process_notes/tf/test.sh) to check whether the tests fail approprietly on the buggy code.  Once you got it to work move to the next step.

10. Test the fixing commit

	* ``docker run -it b4dc23c`` (opens interactively, good for debugging)

	* apply the fix, compile and run tests with [./tests-with-fix.sh](file:///home/wasowski/Dropbox/Notes/20160318_ICT_26_ROSIN/42_bugs_in_ROS/process_notes/tf/tests-with-fix.sh) 

	* You may need to iterate a few times between this and the previous step.

11. To speed things up, I usually combine the last three steps into something like that (kept in my bash history):

	a. to test without a fix quickly run::

       ``docker build -t b4dc23c . && docker run -it b4dc23c ./test.sh``

       b. to test with a fix quickly run: 

       ``docker build -t b4dc23c . && docker run -it b4dc23c ./test-with-fix.sh``. 

       I also keep the command generating the bu_witness.patch in the history, so that it takes two history hits to run a rebuild + test cycle (I guess you can automate this further).

12. Revise the bug description to match the problem: now you really understand what the bug is, so please read the description file and fix any inaccuracies

13. Consider creating the  L2 bug - now you really understand how to do this.

14. If you failed to reproduce, document why (perhaps we need a description extension in the bug file)

# Working with Docker without Bugzoo

(outdated) These are the old commands for running the test on the buggy code and on the fixed code (update pending).

```docker build -t b4dc23c . && docker run -it b4dc23c ./test.sh``` ← should result in a failed test

```docker build -t b4dc23c . && docker run -it b4dc23c ./test-with-fix.sh``` ← should result in a pass (despite some nodes failing, as expected)

<!--- vim:wrap
--->
