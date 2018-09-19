#!/bin/bash
set -e

# Copyright (c) 2018, G.A. vd. Hoorn
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# assumption: 'special' version of rosdistro_build_cache is available
#
# args:
#
#  1: url OR <iso 8601 date+timestamp>
#  2: bug id
#  3: ros distro
#  4: buggy package
#  5: output rosinstall filename

if [ $# -ne 5 ];
then
    echo "USAGE: $0 [ ISSUE_URL | ISO8601_DATETIME ] BUG_ID ROS_DISTRO PUT ROSINSTALL_FILENAME"
    exit 64   # EX_USAGE
fi

SCRIPT_DIR=$(dirname $(readlink -f $0))
ROSDISTRO_DIR=rosdistro

if [ ! -d ${ROSDISTRO_DIR} ];
then
    echo "Need to clone rosdistro .."
    git clone https://github.com/ros/rosdistro.git ${ROSDISTRO_DIR}
fi
git -C ${ROSDISTRO_DIR} checkout -- .
git -C ${ROSDISTRO_DIR} checkout master


BUG_ISSUE_URL=$1

if [[ $BUG_ISSUE_URL = *"http"* ]];
then
    echo "Retrieving issue 'created_at' property for: ${BUG_ISSUE_URL}"
    BUG_STAMP=$(${SCRIPT_DIR}/get_issue_creation_date.py ${BUG_ISSUE_URL})
    echo "Found: ${BUG_STAMP}"
else
    echo "Going back to '${1}'"
    BUG_STAMP=$1
fi

if ! date -d ${BUG_STAMP} &> /dev/null;
then
    echo "Provided date '${BUG_STAMP}' is not a valid date .."
    exit 64   # EX_USAGE
fi

# check to make sure we're not going back to a point earlier than what we support
if [ $(date --date=${BUG_STAMP} +%s) -lt $(date --date='2014-01-25T00:00:00Z' +%s) ];
then
    echo "Date '${BUG_STAMP}' too far in the past."
    exit 64   # EX_USAGE
fi

BUG_ID=$2
BUG_DISTRO=$3
BUG_PKG=$4
BUG_ROSINSTALL_OUTPUT=$5

BUG_ROSDISTRO_COMMIT=$(git -C ${ROSDISTRO_DIR} rev-list -n1 --before=${BUG_STAMP} master)
BUG_ROSDISTRO_CACHE_DIR=$(TZ="UTC" date -d ${BUG_STAMP} +%Y%m%d_%H%M%S)_${BUG_DISTRO}_${BUG_ROSDISTRO_COMMIT:0:8}
echo "Determined rosdistro commit: ${BUG_ROSDISTRO_COMMIT}"


# https://stackoverflow.com/a/41991368
# Note: we don't create tags for efficiency reasons, but to make doing all
# of this manually easier.
BUG_ROSDISTRO_TAG_NAME=bughunt_${BUG_ID}_${BUG_ROSDISTRO_COMMIT:0:8}
if git -C ${ROSDISTRO_DIR} show-ref --quiet refs/tags/${BUG_ROSDISTRO_TAG_NAME};
then
    echo "Reusing existing tag '${BUG_ROSDISTRO_TAG_NAME}'"
else
    echo "Going back in rosdistro's history .."
    echo "Creating tag: '${BUG_ROSDISTRO_TAG_NAME}'"
    git -C ${ROSDISTRO_DIR} tag -am "ROBUST time machine tagging ${BUG_ROSDISTRO_COMMIT:0:8} for ${BUG_STAMP}." ${BUG_ROSDISTRO_TAG_NAME} ${BUG_ROSDISTRO_COMMIT}
fi
git -C ${ROSDISTRO_DIR} checkout -q ${BUG_ROSDISTRO_TAG_NAME}

if [ ! -d ${BUG_ROSDISTRO_CACHE_DIR} ] || [ ! -f ${BUG_ROSDISTRO_CACHE_DIR}/${BUG_DISTRO}-cache.yaml ];
then
    echo "Building cache .."
    rosdistro_build_cache --ignore-local --ignore-errors ${ROSDISTRO_DIR}/index.yaml ${BUG_DISTRO}

    echo "Storing cache in: ${BUG_ROSDISTRO_CACHE_DIR}"
    mkdir -p ${BUG_ROSDISTRO_CACHE_DIR}
    mv ${BUG_DISTRO}-cache.yaml* ${BUG_ROSDISTRO_CACHE_DIR}

else
    echo "Skipping rosdistro cache, already exists"
fi


echo "Updating temporary rosdistro index .."
# recent indices
sed -i "s|http://repositories.ros.org/rosdistro_cache|file://$(pwd)/${BUG_ROSDISTRO_CACHE_DIR}|g" ${ROSDISTRO_DIR}/index.yaml
# old indices
sed -i "s|http://ros.org/rosdistro|file://$(pwd)/${BUG_ROSDISTRO_CACHE_DIR}|g" ${ROSDISTRO_DIR}/index.yaml

echo "Using temporary index to generate rosinstall file (dependencies only) .."
ROSDISTRO_INDEX_URL=file://$(pwd)/${ROSDISTRO_DIR}/index.yaml \
  rosinstall_generator \
    ${BUG_PKG} \
    --rosdistro=${BUG_DISTRO} \
    --deps-only \
    --deps \
    --tar \
    --flat > ${BUG_ROSINSTALL_OUTPUT}


echo "Storing metadata .."
cat << EOF > metadata_${BUG_PKG}_${BUG_DISTRO}_${BUG_ID}.yaml
%YAML 1.1
---
bug_id: ${BUG_ID}
put: ${BUG_PKG}
ros_distro: ${BUG_DISTRO}
datetime_reported: ${BUG_STAMP}
issue_url: ${BUG_ISSUE_URL}
reproduction-images:
  buggy: TODO
  fixed: TODO
  rosdistro: ${BUG_ROSDISTRO_COMMIT}
EOF

echo "Done"
