"""Headless VRX simulation with my world and my WAM-V.

    ros2 launch /ws/launch/sim.launch.py [world:=solent_open_water] [viz:=true]
                                         [x:=0] [y:=0] [yaw:=0]

It uses VRX's own launch helpers (vrx_gz.launch) to start:
- Gazebo headless with a world from worlds/ (open water off Spithead by default),
- my WAM-V (models/wamv_solent.urdf.xacro: GNSS and IMU only, no cameras),
  spawned at x, y (metres east and north of the world origin) and yaw
  (radians, 0 = bow pointing east), plus VRX's ROS 2 bridges;
- a fixed transform from the model frame Gazebo publishes ("wamv") to the
  root of the robot description ("wamv/wamv/base_link"), so viewers can place
  the boat's 3D model in the world,
- foxglove_bridge on port 8765 when viz:=true, for Lichtblick.
"""
import os

from launch import LaunchDescription
import vrx_gz.launch
from vrx_gz.model import Model
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, OpaqueFunction
from launch.launch_description_sources import AnyLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node
from ament_index_python.packages import get_package_share_directory

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup(context):
    world = LaunchConfiguration("world").perform(context)
    viz = LaunchConfiguration("viz").perform(context).lower() == "true"

    pose = [float(LaunchConfiguration(k).perform(context)) for k in ("x", "y")]
    yaw = float(LaunchConfiguration("yaw").perform(context))

    wamv = Model("wamv", "wam-v", [*pose, 0.0, 0.0, 0.0, yaw])
    wamv.set_urdf(os.path.join(REPO, "models", "wamv_solent.urdf.xacro"))

    actions = [
        *vrx_gz.launch.simulation(os.path.join(REPO, "worlds", world), headless=True),
        *vrx_gz.launch.spawn("full", world, [wamv]),
        *vrx_gz.launch.competition_bridges(world),
        Node(package="tf2_ros", executable="static_transform_publisher",
             arguments=["--frame-id", "wamv", "--child-frame-id", "wamv/wamv/base_link"],
             parameters=[{"use_sim_time": True}]),
    ]
    if viz:
        actions.append(IncludeLaunchDescription(
            AnyLaunchDescriptionSource(os.path.join(
                get_package_share_directory("foxglove_bridge"), "launch",
                "foxglove_bridge_launch.xml")),
            launch_arguments={"port": "8765", "use_sim_time": "true"}.items()))
    return actions


def generate_launch_description():
    return LaunchDescription([
        DeclareLaunchArgument("world", default_value="solent_open_water",
                              description="World file in worlds/, without .sdf"),
        DeclareLaunchArgument("viz", default_value="false",
                              description="Start foxglove_bridge for Lichtblick"),
        DeclareLaunchArgument("x", default_value="0.0", description="Spawn x (m, east)"),
        DeclareLaunchArgument("y", default_value="0.0", description="Spawn y (m, north)"),
        DeclareLaunchArgument("yaw", default_value="0.0", description="Spawn heading (rad, 0 = east)"),
        OpaqueFunction(function=setup),
    ])
