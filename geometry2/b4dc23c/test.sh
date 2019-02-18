#!/bin/sh
# rebuild the tests if needed
catkin_make --only-pkg-with-deps=tf2_ros --make-args tests
# this is the actual test call
# rostest tf2_ros bug_witness.test
