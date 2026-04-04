from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    return LaunchDescription(
        [
            IncludeLaunchDescription(
                PythonLaunchDescriptionSource(
                    PathJoinSubstitution([FindPackageShare("joint_bringup"), "launch", "baseline_minimal.launch.py"])
                ),
                launch_arguments={
                    "mode": "controller_integration",
                    "reference_source": "guidance",
                }.items(),
            )
        ]
    )
