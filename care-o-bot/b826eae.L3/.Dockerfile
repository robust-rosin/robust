ARG ROS_DISTRO
ARG UBUNTU_VERSION
ARG USE_APT_OLD_RELEASES
FROM ubuntu:${UBUNTU_VERSION}

# fix the package sources list to use archival sources
# https://askubuntu.com/questions/1000291/error-the-repository-xxx-does-not-have-a-release-file
# https://askubuntu.com/questions/91815/how-to-install-software-or-upgrade-from-an-old-unsupported-release
RUN if [ "${USE_APT_OLD_RELEASES}" = "yes" ]; then \
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
 && pip install setuptools \
 && pip install --upgrade pip \
 && pip install --upgrade \
      wheel \
      rosdep \
      wstool \
      rosinstall \
      rospkg \
      catkin_pkg \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# setup workspace and import packages
WORKDIR ${ROS_WSPACE}
ADD deps.rosinstall ${ROS_WSPACE}
RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/deps.rosinstall

# install system dependencies
#
#   E: Unable to locate package gazebo2
#   ERROR: the following rosdeps failed to install
#     apt: command [apt-get install -y gazebo2] failed
#
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
 && make \
 && make install

# build workspace and install source-based dependencies
RUN ${ROS_WSPACE}/src/catkin/bin/catkin_make_isolated \
      --install \
      --install-space /opt/ros/${ROS_DISTRO} \
      -DCMAKE_BUILD_TYPE=Release \
 && rm -rf \
       ${ROS_WSPACE}/src \
       ${ROS_WSPACE}/build_isolated \
       ${ROS_WSPACE}/devel_isolated

# # download & build Package Under Test
# ADD puts.rosinstall ${ROS_WSPACE}
# RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/puts.rosinstall
# 
# 
# # dependencies should already have been resolved, built and installed, so we
# # can skip running rosdep here. We do of course depend on the package author
# # to have correctly listed all dependencies ..
# 
# 
# # proceed with building the workspace, which now only contains the
# # package(s) under test.
# #
# # Note: need to add 'true' or Docker will fail the build of the image
# # Note2: using '--only-pkg-with-deps' here to avoid building /everything/
# RUN /bin/bash -c '\
#          source /opt/ros/$ROS_DISTRO/setup.bash \
#       && catkin_make --only-pkg-with-deps=roscpp'
# 
# 
# # setup container entrypoints
# COPY ./ros_entrypoint.sh /
# ENTRYPOINT ["/ros_entrypoint.sh"]
# CMD ["bash"]
