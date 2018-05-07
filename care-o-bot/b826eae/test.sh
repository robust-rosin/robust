#!/bin/sh
# rebuild the tests if needed
catkin_make --only-pkg-with-deps=cob_hardware_config --make-args tests
# this is the actual test call
catkin_make run_tests

#RESULT
#$ catkin_test_results build/test_results
#cob_hardware_config/roslaunch-check_common__ROBOT_cob3-9.xml: 1 tests, 0 errors, 1 failures
#cob_hardware_config/roslaunch-check_common__ROBOT_raw3-1.xml: 1 tests, 0 errors, 1 failures
#cob_hardware_config/roslaunch-check_common__robot_cob3-9.xml: 1 tests, 0 errors, 1 failures
#cob_hardware_config/roslaunch-check_common__robot_raw3-1.xml: 1 tests, 0 errors, 1 failures
#Summary: 60 tests, 0 errors, 4 failures
