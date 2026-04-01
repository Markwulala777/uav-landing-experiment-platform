import json
import math
import os

from geometry_msgs.msg import PoseStamped, TwistStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


def quat_conjugate(q):
    return [-q[0], -q[1], -q[2], q[3]]


def rotate_vector(q, vector):
    x, y, z, w = q
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z

    return [
        (1.0 - 2.0 * (yy + zz)) * vector[0] + 2.0 * (xy - wz) * vector[1] + 2.0 * (xz + wy) * vector[2],
        2.0 * (xy + wz) * vector[0] + (1.0 - 2.0 * (xx + zz)) * vector[1] + 2.0 * (yz - wx) * vector[2],
        2.0 * (xz - wy) * vector[0] + 2.0 * (yz + wx) * vector[1] + (1.0 - 2.0 * (xx + yy)) * vector[2],
    ]


class TruthFrameAudit(Node):
    def __init__(self):
        super().__init__("truth_frame_audit")
        self.deck_pose = None
        self.target_pose = None
        self.target_twist = None
        self.uav_pose = None
        self.uav_twist = None
        self.relative_pose = None
        self.relative_twist = None
        self.output_dir = None
        self.report_written = False

        self.declare_parameter("expected_target_offset_xyz", [0.5, 0.0, 0.0])
        self.declare_parameter("target_offset_tolerance", 0.05)
        self.declare_parameter("relative_position_tolerance", 0.05)
        self.declare_parameter("relative_velocity_tolerance", 0.1)

        self.status_pub = self.create_publisher(Bool, "/frame_audit/status/passed", 10)
        self.report_pub = self.create_publisher(String, "/frame_audit/status/report", 10)

        self.create_subscription(PoseStamped, "/deck_interface/truth/deck_pose", self.deck_pose_cb, 10)
        self.create_subscription(PoseStamped, "/deck_interface/truth/landing_target_pose", self.target_pose_cb, 10)
        self.create_subscription(TwistStamped, "/deck_interface/truth/landing_target_twist", self.target_twist_cb, 10)
        self.create_subscription(PoseStamped, "/deck_interface/truth/uav_pose", self.uav_pose_cb, 10)
        self.create_subscription(TwistStamped, "/deck_interface/truth/uav_twist", self.uav_twist_cb, 10)
        self.create_subscription(PoseStamped, "/relative_estimation/truth/relative_pose", self.relative_pose_cb, 10)
        self.create_subscription(TwistStamped, "/relative_estimation/truth/relative_twist", self.relative_twist_cb, 10)
        self.create_subscription(String, "/experiment_manager/output_dir", self.output_dir_cb, 10)

        self.timer = self.create_timer(1.0, self.evaluate)
        self.get_logger().info("frame_audit truth node is running.")

    def deck_pose_cb(self, msg):
        self.deck_pose = msg

    def target_pose_cb(self, msg):
        self.target_pose = msg

    def target_twist_cb(self, msg):
        self.target_twist = msg

    def uav_pose_cb(self, msg):
        self.uav_pose = msg

    def uav_twist_cb(self, msg):
        self.uav_twist = msg

    def relative_pose_cb(self, msg):
        self.relative_pose = msg

    def relative_twist_cb(self, msg):
        self.relative_twist = msg

    def output_dir_cb(self, msg):
        self.output_dir = msg.data

    def evaluate(self):
        if not all(
            [
                self.deck_pose,
                self.target_pose,
                self.target_twist,
                self.uav_pose,
                self.uav_twist,
                self.relative_pose,
                self.relative_twist,
            ]
        ):
            return

        expected_offset = list(self.get_parameter("expected_target_offset_xyz").value)
        target_offset_tolerance = float(self.get_parameter("target_offset_tolerance").value)
        relative_position_tolerance = float(self.get_parameter("relative_position_tolerance").value)
        relative_velocity_tolerance = float(self.get_parameter("relative_velocity_tolerance").value)

        deck_q = [
            self.deck_pose.pose.orientation.x,
            self.deck_pose.pose.orientation.y,
            self.deck_pose.pose.orientation.z,
            self.deck_pose.pose.orientation.w,
        ]
        target_q = [
            self.target_pose.pose.orientation.x,
            self.target_pose.pose.orientation.y,
            self.target_pose.pose.orientation.z,
            self.target_pose.pose.orientation.w,
        ]
        target_q_inv = quat_conjugate(target_q)

        target_delta_world = [
            self.target_pose.pose.position.x - self.deck_pose.pose.position.x,
            self.target_pose.pose.position.y - self.deck_pose.pose.position.y,
            self.target_pose.pose.position.z - self.deck_pose.pose.position.z,
        ]
        target_delta_deck = rotate_vector(quat_conjugate(deck_q), target_delta_world)

        world_relative_position = [
            self.uav_pose.pose.position.x - self.target_pose.pose.position.x,
            self.uav_pose.pose.position.y - self.target_pose.pose.position.y,
            self.uav_pose.pose.position.z - self.target_pose.pose.position.z,
        ]
        world_relative_velocity = [
            self.uav_twist.twist.linear.x - self.target_twist.twist.linear.x,
            self.uav_twist.twist.linear.y - self.target_twist.twist.linear.y,
            self.uav_twist.twist.linear.z - self.target_twist.twist.linear.z,
        ]

        relative_position_target = rotate_vector(target_q_inv, world_relative_position)
        relative_velocity_target = rotate_vector(target_q_inv, world_relative_velocity)

        target_offset_error = math.sqrt(
            sum((target_delta_deck[i] - expected_offset[i]) ** 2 for i in range(3))
        )
        relative_position_error = math.sqrt(
            (relative_position_target[0] - self.relative_pose.pose.position.x) ** 2
            + (relative_position_target[1] - self.relative_pose.pose.position.y) ** 2
            + (relative_position_target[2] - self.relative_pose.pose.position.z) ** 2
        )
        relative_velocity_error = math.sqrt(
            (relative_velocity_target[0] - self.relative_twist.twist.linear.x) ** 2
            + (relative_velocity_target[1] - self.relative_twist.twist.linear.y) ** 2
            + (relative_velocity_target[2] - self.relative_twist.twist.linear.z) ** 2
        )

        passed = (
            target_offset_error <= target_offset_tolerance
            and relative_position_error <= relative_position_tolerance
            and relative_velocity_error <= relative_velocity_tolerance
        )

        report = {
            "passed": passed,
            "target_offset_error": target_offset_error,
            "relative_position_error": relative_position_error,
            "relative_velocity_error": relative_velocity_error,
            "expected_target_offset_xyz": expected_offset,
            "measured_target_offset_in_deck_frame_xyz": target_delta_deck,
        }

        self.status_pub.publish(Bool(data=passed))
        self.report_pub.publish(String(data=json.dumps(report, sort_keys=True)))

        if self.output_dir and not self.report_written:
            try:
                os.makedirs(self.output_dir, exist_ok=True)
                with open(os.path.join(self.output_dir, "frame_audit_report.json"), "w", encoding="utf-8") as handle:
                    json.dump(report, handle, indent=2, sort_keys=True)
                self.report_written = True
            except OSError as exc:
                self.get_logger().warn(f"Failed to write frame audit report: {exc}")


def main():
    rclpy.init()
    node = TruthFrameAudit()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
