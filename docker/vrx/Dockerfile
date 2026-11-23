# VRX (Virtual RobotX) on ROS 2 Jazzy + Gazebo Harmonic, built from source so it
# runs natively on arm64 (my Mac) as well as amd64 (CI).
# Gazebo comes from the ROS vendor packages (gz_*_vendor), which pair Jazzy
# with Harmonic, so I don't need the OSRF Gazebo apt repository.
FROM ros:jazzy-ros-base

ARG VRX_VERSION=v3.1.2
ENV DEBIAN_FRONTEND=noninteractive
# Retry downloads: Ubuntu's mirrors are sometimes slow or drop connections.
RUN echo 'Acquire::Retries "5";' > /etc/apt/apt.conf.d/80-retries

RUN apt-get update && apt-get install -y --no-install-recommends \
      git \
      ros-jazzy-ros-gz \
      ros-jazzy-foxglove-bridge \
      python3-pytest \
    && rm -rf /var/lib/apt/lists/*

# VRX from a fixed release tag.
RUN mkdir -p /opt/vrx_ws/src \
    && git clone --depth 1 --branch ${VRX_VERSION} https://github.com/osrf/vrx.git /opt/vrx_ws/src/vrx \
    && apt-get update \
    && . /opt/ros/jazzy/setup.sh \
    && rosdep install -r -y --from-paths /opt/vrx_ws/src --ignore-src --rosdistro jazzy \
    && rm -rf /var/lib/apt/lists/*

RUN . /opt/ros/jazzy/setup.sh \
    && cd /opt/vrx_ws \
    && colcon build --merge-install --cmake-args -DCMAKE_BUILD_TYPE=Release \
    && rm -rf build log

# Every shell (interactive or not) sees ROS and VRX.
RUN echo "source /opt/vrx_ws/install/setup.bash" >> /etc/bash.bashrc
ENV BASH_ENV=/opt/vrx_ws/install/setup.bash
# Each container runs its own simulation: only discover ROS nodes inside it,
# so two simulations on the same machine never see each other's topics.
ENV ROS_AUTOMATIC_DISCOVERY_RANGE=LOCALHOST

WORKDIR /ws
