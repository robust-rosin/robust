# this file is just here whilst I get things working: we should move to
# BugZoo in the long term.
BUG=ca23e58
ROS_DISTRO=kinetic #lunar
UBUNTU_VERSION=xenial #17.04
USE_APT_OLD_RELEASES=yes
IS_BUILD_FAILURE=no

# BUG=b826eae
# ROS_DISTRO=indigo
# UBUNTU_VERSION=14.04
# USE_APT_OLD_RELEASES=no

L3_DIR="${BUG}.L3"
cp Dockerfile "${L3_DIR}/.Dockerfile"
docker build --build-arg UBUNTU_VERSION="${UBUNTU_VERSION}" \
             --build-arg ROS_DISTRO="${ROS_DISTRO}" \
             --build-arg IS_BUILD_FAILURE="${IS_BUILD_FAILURE}" \
             -f "${L3_DIR}/.Dockerfile" \
             -t cool "${BUG}.L3"
rm -f "${L3_DIR}/.Dockerfile"
