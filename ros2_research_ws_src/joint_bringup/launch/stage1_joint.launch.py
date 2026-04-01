from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.actions import SetParameter
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    scenario_config = LaunchConfiguration("scenario_config")
    output_root = LaunchConfiguration("output_root")
    run_id = LaunchConfiguration("run_id")
    seed = LaunchConfiguration("seed")
    scenario_id = LaunchConfiguration("scenario_id")
    sea_state = LaunchConfiguration("sea_state")

    return LaunchDescription(
        [
            DeclareLaunchArgument("scenario_config", default_value="calm_truth.yaml"),
            DeclareLaunchArgument("output_root", default_value="~/uav-usv-experiment-runs"),
            DeclareLaunchArgument("run_id", default_value=""),
            DeclareLaunchArgument("seed", default_value="42"),
            DeclareLaunchArgument("scenario_id", default_value="calm_truth"),
            DeclareLaunchArgument("sea_state", default_value="calm"),
            SetParameter(name="use_sim_time", value=True),
            Node(
                package="experiment_manager",
                executable="scenario_runner",
                name="experiment_manager",
                output="screen",
                parameters=[
                    PathJoinSubstitution([FindPackageShare("joint_bringup"), "config", scenario_config]),
                    {
                        "output_root": output_root,
                        "run_id": run_id,
                        "seed": seed,
                        "scenario_id": scenario_id,
                        "sea_state": sea_state,
                    },
                ],
            ),
            Node(
                package="deck_description",
                executable="deck_geometry",
                name="deck_description",
                output="screen",
            ),
            Node(
                package="deck_interface",
                executable="truth_relay",
                name="deck_interface",
                output="screen",
            ),
            Node(
                package="relative_estimation",
                executable="truth_relative_state",
                name="relative_estimation",
                output="screen",
            ),
            Node(
                package="safety_manager",
                executable="truth_safety_monitor",
                name="safety_manager",
                output="screen",
                parameters=[PathJoinSubstitution([FindPackageShare("joint_bringup"), "config", scenario_config])],
            ),
            Node(
                package="touchdown_manager",
                executable="truth_touchdown_monitor",
                name="touchdown_manager",
                output="screen",
            ),
            Node(
                package="landing_guidance",
                executable="truth_guidance",
                name="landing_guidance",
                output="screen",
                parameters=[PathJoinSubstitution([FindPackageShare("joint_bringup"), "config", scenario_config])],
            ),
            Node(
                package="landing_guidance",
                executable="px4_offboard_bridge",
                name="px4_offboard_bridge",
                output="screen",
            ),
            Node(
                package="frame_audit",
                executable="truth_frame_audit",
                name="frame_audit",
                output="screen",
            ),
            Node(
                package="metrics_evaluator",
                executable="summary_writer",
                name="metrics_evaluator",
                output="screen",
            ),
        ]
    )
