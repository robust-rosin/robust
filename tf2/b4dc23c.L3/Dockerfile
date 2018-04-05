FROM ubuntu:14.04.5

ENV DEBIAN_FRONTEND=noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8

# TODO: use local mirror to speed things up
# RUN sed -i 's|archive.ubuntu.com/ubuntu/|ftp.tudelft.nl/archive.ubuntu.com/|g' /etc/apt/sources.list

# add bootstrap utils/progs
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      python-pip \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# add bootstrap ros utils
RUN pip install -U rosdep wstool rosinstall rospkg catkin_pkg

# setup workspace and import packages
WORKDIR /ros_ws
ADD pkgs.rosinstall /ros_ws/
RUN wstool init -j8 /ros_ws/src /ros_ws/pkgs.rosinstall

# install system deps
RUN apt-get update \
 && rosdep init \
 && rosdep update \
 && rosdep install --from-paths src -i --rosdistro=indigo -y --skip-keys="python-rosdep python-catkin-pkg python-rospkg" \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# build workspace
RUN /ros_ws/src/catkin/bin/catkin_make_isolated \
      --install \
      --install-space /opt/ros/indigo 
#      -DCMAKE_BUILD_TYPE=Release

# prevents some file system errors with readonly log dirs
RUN mkdir -pv logs
ENV ROS_LOG_DIR=/ros_ws/logs/

# move in the bug reproduction setup (test, assertion, etc.) 
ADD bug_witness.patch /ros_ws/
ADD fix.patch /ros_ws/
ADD fix.sh /ros_ws/
ADD test.sh /ros_ws/
ADD test-with-fix.sh /ros_ws/
# apply the bug witness test patch so that the tree is ready for testing
RUN patch -p1 -d src/ <bug_witness.patch

# compile tests so that we are ready to run on start (this saves a bit of time if cached)
RUN /ros_ws/src/catkin/bin/catkin_make_isolated --pkg tf2_ros --make-args tests

# setup container entrypoints
COPY ./entrypoint.sh /
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]


