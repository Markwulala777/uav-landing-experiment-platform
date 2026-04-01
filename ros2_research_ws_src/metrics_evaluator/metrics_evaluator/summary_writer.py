import csv
import json
import math
import os
from time import monotonic

from geometry_msgs.msg import PoseStamped, TwistStamped
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


class SummaryWriter(Node):
    def __init__(self):
        super().__init__("metrics_evaluator")
        self.relative_pose = None
        self.relative_twist = None
        self.phase = "initializing"
        self.safety_reason = "unknown"
        self.abort_requested = False
        self.touchdown_detected = False
        self.outcome_label = "pending"
        self.max_xy_error = 0.0
        self.run_id = "unassigned"
        self.scenario_id = "unknown"
        self.output_dir = None
        self.summary_written = False
        self.start_monotonic = monotonic()
        self.sample_count = 0

        self.summary_ready_pub = self.create_publisher(Bool, "/metrics_evaluator/status/summary_ready", 10)

        self.create_subscription(PoseStamped, "/relative_estimation/truth/relative_pose", self.relative_pose_cb, 10)
        self.create_subscription(TwistStamped, "/relative_estimation/truth/relative_twist", self.relative_twist_cb, 10)
        self.create_subscription(String, "/landing_guidance/status/phase", self.phase_cb, 10)
        self.create_subscription(String, "/safety_manager/status/reason", self.safety_reason_cb, 10)
        self.create_subscription(Bool, "/safety_manager/status/abort_requested", self.abort_requested_cb, 10)
        self.create_subscription(Bool, "/touchdown_manager/status/touchdown_detected", self.touchdown_detected_cb, 10)
        self.create_subscription(String, "/touchdown_manager/status/outcome_label", self.outcome_label_cb, 10)
        self.create_subscription(String, "/experiment_manager/run_id", self.run_id_cb, 10)
        self.create_subscription(String, "/experiment_manager/scenario_id", self.scenario_id_cb, 10)
        self.create_subscription(String, "/experiment_manager/output_dir", self.output_dir_cb, 10)

        self.timer = self.create_timer(1.0, self.maybe_write_summary)
        self.get_logger().info("metrics_evaluator summary writer is running.")

    def relative_pose_cb(self, msg):
        self.relative_pose = msg
        xy_error = math.hypot(msg.pose.position.x, msg.pose.position.y)
        self.max_xy_error = max(self.max_xy_error, xy_error)
        self.sample_count += 1

    def relative_twist_cb(self, msg):
        self.relative_twist = msg

    def phase_cb(self, msg):
        self.phase = msg.data

    def safety_reason_cb(self, msg):
        self.safety_reason = msg.data

    def abort_requested_cb(self, msg):
        self.abort_requested = msg.data

    def touchdown_detected_cb(self, msg):
        self.touchdown_detected = msg.data

    def outcome_label_cb(self, msg):
        self.outcome_label = msg.data

    def run_id_cb(self, msg):
        self.run_id = msg.data

    def scenario_id_cb(self, msg):
        self.scenario_id = msg.data

    def output_dir_cb(self, msg):
        self.output_dir = msg.data

    def maybe_write_summary(self):
        if self.summary_written or not self.output_dir or self.relative_pose is None or self.relative_twist is None:
            self.summary_ready_pub.publish(Bool(data=self.summary_written))
            return

        should_write = self.touchdown_detected or self.abort_requested
        if not should_write:
            self.summary_ready_pub.publish(Bool(data=False))
            return

        os.makedirs(self.output_dir, exist_ok=True)

        summary = {
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "phase": self.phase,
            "safety_reason": self.safety_reason,
            "abort_requested": self.abort_requested,
            "touchdown_detected": self.touchdown_detected,
            "outcome_label": self.outcome_label,
            "max_xy_error_m": self.max_xy_error,
            "final_xy_error_m": math.hypot(self.relative_pose.pose.position.x, self.relative_pose.pose.position.y),
            "final_z_error_m": self.relative_pose.pose.position.z,
            "final_lateral_speed_mps": math.hypot(
                self.relative_twist.twist.linear.x,
                self.relative_twist.twist.linear.y,
            ),
            "final_vertical_speed_mps": abs(self.relative_twist.twist.linear.z),
            "samples": self.sample_count,
            "time_to_event_s": monotonic() - self.start_monotonic,
        }

        with open(os.path.join(self.output_dir, "summary.json"), "w", encoding="utf-8") as handle:
            json.dump(summary, handle, indent=2, sort_keys=True)

        csv_path = os.path.join(self.output_dir, "summary.csv")
        with open(csv_path, "w", encoding="utf-8", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=list(summary.keys()))
            writer.writeheader()
            writer.writerow(summary)

        self.summary_written = True
        self.summary_ready_pub.publish(Bool(data=True))


def main():
    rclpy.init()
    node = SummaryWriter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
