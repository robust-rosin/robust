# TODO explain build-time arguments
#
# Build Arguments:
#
#   ROS_DISTRO -- the name of the ROS distribution that should be used when
#     replicating the bug.
#   UBUNTU_VERSION -- the version of Ubuntu that should be used when
#     replicating the bug; should be given as a numbered version to avoid
#     non-deterministic build outcomes.
#   USE_APT_OLD_RELEASES -- a flag that accepts the values "True" or "False".
#     If set to true, the resulting Docker image will attempt to use archival
#     package sources. Allows "apt-get" to be used with versions of Ubuntu
#     that are no longer maintained.
#   CATKIN_PKG -- the local name of the package under test (i.e., the name
#     of the directory inside "source" that will contain the source code for
#     the package under test).
#
ARG ROS_DISTRO
ARG UBUNTU_VERSION
FROM ubuntu:${UBUNTU_VERSION}

# fix the package sources list to use archival sources
# https://askubuntu.com/questions/1000291/error-the-repository-xxx-does-not-have-a-release-file
# https://askubuntu.com/questions/91815/how-to-install-software-or-upgrade-from-an-old-unsupported-release
ARG USE_APT_OLD_RELEASES
RUN if [ "${USE_APT_OLD_RELEASES}" = "True" ]; then \
      sed -i -re 's/([a-z]{2}\.)?archive.ubuntu.com|security.ubuntu.com/old-releases.ubuntu.com/g' \
        /etc/apt/sources.list \
      && apt-get update \
      && apt-get dist-upgrade \
    ; fi

ENV ROS_WSPACE=/ros_ws
ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# install bootstrap utilities
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      git \
      python-pip \
      cmake \
      wget \
      lsb-release \
 && pip install --upgrade pip==9.0.3 \
 && pip install setuptools \
 && pip install --upgrade \
      wheel \
      rosdep \
      wstool \
      rosinstall \
      rospkg \
      catkin_pkg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# add OSRF repository to prevent Gazebo installation problems
RUN echo "deb http://packages.osrfoundation.org/gazebo/ubuntu-stable `lsb_release -cs` main" > /etc/apt/sources.list.d/gazebo-stable.list \
 && wget http://packages.osrfoundation.org/gazebo.key -O - | apt-key add -

# install the following for 17.10: gnupg dirmngr

# setup workspace and import packages
WORKDIR ${ROS_WSPACE}
COPY deps.rosinstall .
RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/deps.rosinstall

# generate fix and unfix scripts
RUN echo "patch -p1 -d '${ROS_WSPACE}/src' < fix.patch" > fix.sh \
 && echo "patch -p1 -R -d '${ROS_WSPACE}/src' < fix.patch" > unfix.sh \
 && chmod +x fix.sh unfix.sh

# install system dependencies
RUN apt-get update \
 && rosdep init \
 && rosdep update \
 && rosdep install --from-paths src -i --rosdistro=${ROS_DISTRO} -y \
      --skip-keys="python-rosdep python-catkin-pkg python-rospkg" \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# install gtest
RUN cd /usr/src/gtest \
 && cmake CMakeLists.txt \
 && make

# build workspace and install source-based dependencies
RUN ${ROS_WSPACE}/src/catkin/bin/catkin_make_isolated \
      --install \
      --install-space /opt/ros/${ROS_DISTRO} \
      -DCMAKE_BUILD_TYPE=Release \
 && rm -rf \
       ${ROS_WSPACE}/src \
       ${ROS_WSPACE}/build_isolated \
       ${ROS_WSPACE}/devel_isolated

# download & build Package Under Test
COPY puts.rosinstall .
RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/puts.rosinstall

# FIXME use branches or tags rather than patches
COPY bug_witness.patch .
RUN patch -p1 -d src < bug_witness.patch

# dependencies should already have been resolved, built and installed, so we
# can skip running rosdep here. We do of course depend on the package author
# to have correctly listed all dependencies ..

# proceed with building the workspace, which now only contains the
# package(s) under test.
# we now attempt to build the workspace, and suppress any errors if the bug is
# expected to be a build failure.
# we use '--only-pkg-with-deps' to avoid building /everything/
ARG IS_BUILD_FAILURE
ARG CATKIN_PKG
RUN echo "#!/bin/bash\n\
          source /opt/ros/$ROS_DISTRO/setup.bash \
          && catkin_make --only-pkg-with-deps=${CATKIN_PKG}" > build.sh \
 && chmod +x build.sh
RUN if [ "${IS_BUILD_FAILURE}" = "False" ]; then ./build.sh ; fi
COPY test.sh .

# add historical patch
# TODO automatically generate (or avoid the need to do so)
COPY fix.patch .

# FIXME move to top of Dockerfile
# setup container entrypoints
RUN echo "#!/bin/bash \n\
set -e \n\
source \"/opt/ros/\${ROS_DISTRO}/setup.bash\" \n\
source \"${ROS_WSPACE}/devel/setup.bash\" \n\
exec \"\$@\"" > /entrypoint.sh \
 && chmod +x /entrypoint.sh
# source \"${ROS_WSPACE}/devel/setup.bash\" \n\
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]
