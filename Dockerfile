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
##############################################################################
FROM alpine:3.7 as fork
ARG REPO_FORK_URL
RUN apk --no-cache add git
RUN echo "[ROBUST] cloning repo: '${REPO_FORK_URL}'" \
 && git clone "${REPO_FORK_URL}" /repo-under-test \
 && cd /repo-under-test \
 && git config remote.origin.fetch "+refs/heads/*:refs/remotes/origin/*" \
 && echo "[ROBUST] cloned repo."
ARG REPO_FIX_COMMIT
ARG REPO_BUG_COMMIT
RUN cd /repo-under-test \
 && echo "[ROBUST] fetching latest buggy and fixed verisons..." \
 && echo "[ROBUST] fetching bug version: ${REPO_BUG_COMMIT}" \
 && echo "[ROBUST] fetching fix version: ${REPO_FIX_COMMIT}" \
 && git fetch --all \
 && echo "[ROBUST] fetched latest buggy and fixed versions." \
 && echo "[ROBUST] generating patch diff..." \
 && git diff "${REPO_BUG_COMMIT}" "${REPO_FIX_COMMIT}" > /fix.patch \
 && echo "[ROBUST] generated patch diff."


##############################################################################
# Build a (reusable) base image for the ROS distro
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

# create an empty workspace
WORKDIR "${ROS_WSPACE}"
RUN mkdir src


##############################################################################
# Build a base image for the PUT that contains its dependencies
##############################################################################
FROM distro as put_base_with_deps
ARG CATKIN_PACKAGES
ENV CATKIN_PACKAGES "${CATKIN_PACKAGES}"
# NOTE assumes catkin >= 0.5.78 (supports --only-pkg-with-deps)
RUN echo "[ROBUST] creating build script" \
 && echo "#!/bin/bash\n\
          source /opt/ros/$ROS_DISTRO/setup.bash \
          && echo '[ROBUST] attempting to build PUT...' \
          && echo \"[ROBUST] building packages: ${CATKIN_PACKAGES}\" \
          && catkin_make --only-pkg-with-deps ${CATKIN_PACKAGES}" > build.sh \
 && chmod +x build.sh \
 && echo "[ROBUST] created build script"

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
 && rm -rf /var/lib/apt/lists/* \
 && cd /usr/src/gtest \
 && cmake CMakeLists.txt \
 && make

# install source dependencies, then destroy workspace
RUN ${ROS_WSPACE}/src/catkin/bin/catkin_make_isolated \
      --install \
      --install-space /opt/ros/${ROS_DISTRO} \
      -DCMAKE_BUILD_TYPE=Release \
 && rm -rf \
       ${ROS_WSPACE}/src \
       ${ROS_WSPACE}/build_isolated \
       ${ROS_WSPACE}/devel_isolated

COPY --from=fork fix.patch fix.patch
COPY --from=fork repo-under-test src/repo-under-test


##############################################################################
# Build an image for the buggy verison of the PUT
##############################################################################
FROM put_base_with_deps as bug
ARG REPO_BUG_COMMIT
ARG IS_BUILD_FAILURE
RUN cd src/repo-under-test \
 && echo "[ROBUST] building buggy PUT..." \
 && echo "[ROBUST] is a build failure expected? ${IS_BUILD_FAILURE}." \
 && echo "[ROBUST] using bug commit: ${REPO_BUG_COMMIT}" \
 && git reset --hard "${REPO_BUG_COMMIT}" \
 && cd "${ROS_WSPACE}" \
 && ./build.sh || [ "${IS_BUILD_FAILURE}" = "yes" ]
COPY test.sh .

##############################################################################
# Build an image for the fixed verison of the PUT
##############################################################################
FROM put_base_with_deps as fix
ARG REPO_FIX_COMMIT
RUN cd src/repo-under-test \
 && echo "[ROBUST] building fixed PUT..." \
 && echo "[ROBUST] using fix commit: ${REPO_FIX_COMMIT}" \
 && git reset --hard "${REPO_FIX_COMMIT}" \
 && cd "${ROS_WSPACE}" \
 && ./build.sh
COPY test.sh .
