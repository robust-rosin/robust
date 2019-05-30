#!/bin/bash
pushd "${ROS_WS}"
catkin_make run_tests
