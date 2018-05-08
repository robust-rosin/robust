#!/bin/sh
# rebuild the tests if needed
catkin_make --only-pkg-with-deps=cob_hardware_config --make-args tests
# this is the actual test call
catkin_make run_tests_cob_hardware_config_roslaunch-check_common__ROBOT_cob3-9
#executes: roslaunch_add_file_check(common robot:=${robot})

