# This Dockerfile is used to construct container images for all of the bugs
# belonging to the ROBUST dataset.
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
#   CATKIN_PACKAGES -- a space-colon-delimited list of the names of the
#     packages under test.
#   REPO_FORK_URL -- the URL of the ROBUST fork Git repository for this bug.
#   REPO_BUG_COMMIT -- the SHA-1 hash for the commit in the forked repository
#     that provides the buggy version of the code. This version of the code
#     also contains supplementary files that, where possible, provide a test
#     case for the bug.
#   REPO_FIX_COMMIT -- the SHA-1 hash for the commit in the forked repository
#     that provides the fixed version of the code. This version of the code
#     also contains supplementary files that, where possible, provide a test
#     case for the bug.
#   IS_BUILD_FAILURE -- indicates whether or not the package under test is
#     expected to encounter a build failure. Accepts values of "True" and
#     "False".
#
ARG UBUNTU_VERSION


##############################################################################
# Download the forked repository as a build stage to improve build caching.
#
# Arguments:
#
# * REPO_FORK_URL
#
##############################################################################
FROM alpine:3.7 as fork
ARG REPO_FORK_URL
RUN apk --no-cache add git
RUN echo "[ROBUST] cloning repo: '${REPO_FORK_URL}'" \
 && git clone "${REPO_FORK_URL}" /tmp/repo-under-test \
 && echo "[ROBUST] cloned repo."


##############################################################################
# Build a (reusable) base image for the ROS distro
#
# Arguments:
#
# * UBUNTU_VERSION
# * ROS_DISTRO
# * USE_APT_OLD_RELEASES
# * USE_OSRF_REPOS
#
##############################################################################
FROM ubuntu:${UBUNTU_VERSION} as distro
ENV ROS_WSPACE /ros_ws
ENV DEBIAN_FRONTEND noninteractive
ENV LANG C.UTF-8
ENV LC_ALL C.UTF-8
ARG ROS_DISTRO
ENV ROS_DISTRO "${ROS_DISTRO}"
RUN echo "[ROBUST]: building image for ROS_DISTRO: '${ROS_DISTRO}'"
RUN echo "#!/bin/bash \n\
set -e \n\
source \"/opt/ros/\${ROS_DISTRO}/setup.bash\" \n\
source \"${ROS_WSPACE}/devel/setup.bash\" \n\
exec \"\$@\"" > /entrypoint.sh \
 && chmod +x /entrypoint.sh
ENTRYPOINT ["/entrypoint.sh"]
CMD ["bash"]

# fix the package sources list to use archival sources
# https://askubuntu.com/questions/1000291/error-the-repository-xxx-does-not-have-a-release-file
# https://askubuntu.com/questions/91815/how-to-install-software-or-upgrade-from-an-old-unsupported-release
ARG USE_APT_OLD_RELEASES
RUN echo "[ROBUST] use archival sources? '${USE_APT_OLD_RELEASES}'" \
 && if [ "${USE_APT_OLD_RELEASES}" = "True" ]; then \
      echo "[ROBUST] using archival sources" \
      && sed -i -re 's/([a-z]{2}\.)?archive.ubuntu.com|security.ubuntu.com/old-releases.ubuntu.com/g' \
        /etc/apt/sources.list \
      && apt-get update \
      && apt-get dist-upgrade \
    ; else \
      echo "[ROBUST] not using archival sources" \
    ; fi

RUN apt-get update \
 && apt-get install -y --no-install-recommends \
      build-essential \
      ca-certificates \
      git \
      python-pip \
      cmake \
      wget \
      lsb-release \
 && pip --version \
 && pip install --upgrade -i https://pypi.python.org/simple pip==9.0.3
RUN pip install --upgrade setuptools
RUN pip install --upgrade \
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
# optionally add packages.ros.org as a source
ARG USE_OSRF_REPOS
RUN if [ "${USE_OSRF_REPOS}" = "True" ]; then \
         echo "deb http://packages.ros.org/ros/ubuntu $(lsb_release -cs) main" > /etc/apt/sources.list.d/ros-latest.list \
       && wget http://packages.ros.org/ros.key -O - | apt-key add - \
    ; fi

# install gtest
RUN cd /usr/src/gtest \
 && cmake CMakeLists.txt \
 && make

# create an empty workspace
WORKDIR "${ROS_WSPACE}"
RUN mkdir src


##############################################################################
# Build an image for the PUT
#
# Arguments:
#
# * REPO_FIX_COMMIT
# * REPO_BUG_COMMIT
# * IS_BUILD_FAILURE
# * CATKIN_PACKAGES
#
##############################################################################
FROM distro as put

# setup workspace and import packages
COPY deps.rosinstall .
RUN wstool init -j8 ${ROS_WSPACE}/src ${ROS_WSPACE}/deps.rosinstall

# install binary dependencies via rosdep
RUN apt-get clean \
 && apt-get update \
 && rosdep init \
 && rosdep update \
 && rosdep install --from-paths src -i --rosdistro=${ROS_DISTRO} -y \
      --skip-keys="python-rosdep python-catkin-pkg python-rospkg" \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

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
COPY --from=fork /tmp/repo-under-test src/repo-under-test
ARG REPO_FIX_COMMIT
ARG REPO_BUG_COMMIT
ENV REPO_FIX_COMMIT "${REPO_FIX_COMMIT}"
ENV REPO_BUG_COMMIT "${REPO_BUG_COMMIT}"
RUN cd src/repo-under-test \
 && echo "[ROBUST] fetching fixed and buggy source code..." \
 && echo "[ROBUST] using fix commit: ${REPO_FIX_COMMIT}" \
 && echo "[ROBUST] using bug commit: ${REPO_BUG_COMMIT}" \
 && git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*" \
 && git fetch --all \
 && git reset --hard "${REPO_BUG_COMMIT}" \
 && echo "[ROBUST] fetched fixed and buggy source code."

# generate fix and unfix scripts
RUN echo "#!/bin/bash\n\
pushd '${ROS_WSPACE}/src/repo-under-test' && \n\
git clean -dfx && \n\
git checkout \"\$1\" && \n\
echo \"switched mode to: \$1\"" > switch \
 && echo "#!/bin/bash\n'${ROS_WSPACE}/switch' \"\${REPO_FIX_COMMIT}\"" > fix \
 && echo "#!/bin/bash\n'${ROS_WSPACE}/switch' \"\${REPO_BUG_COMMIT}\"" > unfix \
 && chmod +x fix unfix switch

# dependencies should already have been resolved, built and installed, so we
# can skip running rosdep here. We do of course depend on the package author
# to have correctly listed all dependencies ..

# proceed with building the workspace, which now only contains the
# package(s) under test.
# we now attempt to build the workspace, and suppress any errors if the bug is
# expected to be a build failure.
# NOTE assumes catkin >= 0.5.78 (supports --only-pkg-with-deps)
ARG CATKIN_PACKAGES
ENV CATKIN_PACKAGES "${CATKIN_PACKAGES}"
RUN echo "[ROBUST] creating build script" \
 && echo "#!/bin/bash\n\
          source /opt/ros/$ROS_DISTRO/setup.bash \
          && catkin_make --only-pkg-with-deps ${CATKIN_PACKAGES}" > build.sh \
 && chmod +x build.sh \
 && echo "[ROBUST] created build script"

ARG IS_BUILD_FAILURE
RUN echo "[ROBUST] attempting to build PUT..." \
 && echo "[ROBUST] building packages: ${CATKIN_PACKAGES}" \
 && echo "[ROBUST] is a build failure expected? ${IS_BUILD_FAILURE}." \
 && ./build.sh || [ "${IS_BUILD_FAILURE}" = "yes" ]
COPY test.sh .

# automatically generate historical patch
RUN cd src/repo-under-test \
 && git diff "${REPO_BUG_COMMIT}" "${REPO_FIX_COMMIT}" > "${ROS_WSPACE}/fix.patch"
