#!/bin/sh
# patch does not reliably apply permission bits
chmod -v +x src/geometry2/tf2_ros/test/bug_witness.sh
# rebuild the tests if needed
/ros_ws/src/catkin/bin/catkin_make_isolated --pkg tf2_ros --make-args tests
# this is the actual test call
rostest tf2_ros bug_witness.test
