#!/bin/bash
docker build -f Dockerfile.L1 -t ros-bugs:1a746c3-L1 .
docker build -f Dockerfile.L3 -t ros-bugs:1a746c3-L3 .
docker build -f Dockerfile.L3 -t example-ros-bug .
