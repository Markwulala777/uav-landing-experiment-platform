from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription(
        [
            Node(
                package="deck_interface",
                executable="truth_relay",
                name="deck_truth_relay",
                output="screen",
            ),
            Node(
                package="relative_estimation",
                executable="truth_relative_state",
                name="truth_relative_state",
                output="screen",
            ),
            Node(
                package="safety_manager",
                executable="truth_safety_monitor",
                name="truth_safety_monitor",
                output="screen",
            ),
            Node(
                package="touchdown_manager",
                executable="truth_touchdown_monitor",
                name="truth_touchdown_monitor",
                output="screen",
            ),
            Node(
                package="landing_guidance",
                executable="truth_guidance",
                name="truth_guidance",
                output="screen",
            ),
        ]
    )
