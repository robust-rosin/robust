#!/bin/bash
set -e

# setup ros environment
source "/opt/ros/indigo/setup.bash"
source "devel_isolated/setup.bash"
exec "$@"
