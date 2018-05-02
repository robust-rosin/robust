FROM ubuntu:16.04

ARG ROS_DISTRO=kinetic

ENV ROS_WSPACE=/ros_ws

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# add OSRF repository
# TODO: could just start from a ros:kinetic image?
#RUN echo "deb http://packages.ros.org/ros/ubuntu xenial main" > /etc/apt/sources.list.d/ros-latest.list \
# && apt-key adv --keyserver hkp://ha.pool.sks-keyservers.net:80 --recv-key 421C365BD9FF1F717815A3895523BAEEB01FA116

# add bootstrap utils/progs
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      git \
      python-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# upgrade and install necessary pip tools/parts
RUN pip install --upgrade pip setuptools wheel

# add bootstrap ros utils
RUN pip install -U rosdep wstool rosinstall rospkg catkin_pkg

# setup workspace and import packages
WORKDIR ${ROS_WSPACE}
ADD deps.rosinstall ${ROS_WSPACE}
RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/deps.rosinstall

# TODO: allow patching some things here?

# install system deps
RUN apt-get update \
 && rosdep init \
 && rosdep update \
 && rosdep install --from-paths src -i --rosdistro=${ROS_DISTRO} -y --skip-keys="python-rosdep python-catkin-pkg python-rospkg" \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# build workspace
RUN ${ROS_WSPACE}/src/catkin/bin/catkin_make_isolated \
      --install \
      --install-space /opt/ros/${ROS_DISTRO} \
      -DCMAKE_BUILD_TYPE=Release

# remove temporaries
RUN rm -rf \
       ${ROS_WSPACE}/src \
       ${ROS_WSPACE}/build_isolated \
       ${ROS_WSPACE}/devel_isolated

# download & build Package Under Test
WORKDIR ${ROS_WSPACE}
ADD puts.rosinstall ${ROS_WSPACE}
RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/puts.rosinstall


# dependencies should already have been resolved, built and installed, so we
# can skip running rosdep here. We do of course depend on the package author
# to have correctly listed all dependencies ..


# proceed with building the workspace, which now only contains the
# package(s) under test.
#
# Note: need to add 'true' or Docker will fail the build of the image
# Note2: using '--only-pkg-with-deps' here to avoid building /everything/
RUN /bin/bash -c '\
         source /opt/ros/$ROS_DISTRO/setup.bash \
      && catkin_make --only-pkg-with-deps=roscpp'


# setup container entrypoints
COPY ./ros_entrypoint.sh /
ENTRYPOINT ["/ros_entrypoint.sh"]
CMD ["bash"]
