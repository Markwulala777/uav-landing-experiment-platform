import csv
import json
import math
import os
from time import monotonic

import rclpy
from rclpy.node import Node
from uav_usv_landing_msgs.msg import (
    ExperimentRunStatus,
    LandingDecisionStatus,
    LandingWindowStatus,
    MetricsSummary,
    MissionStatus,
    RelativeState,
    SafetyStatus,
    TouchdownState,
)


class SummaryWriter(Node):
    def __init__(self):
        super().__init__("metrics_evaluator")
        self.relative_state = None
        self.mission_status = None
        self.safety_status = None
        self.touchdown_state = None
        self.run_status = None
        self.last_decision_advisory = None
        self.max_xy_error = 0.0
        self.summary_written = False
        self.start_monotonic = monotonic()
        self.sample_count = 0
        self.go_around_count = 0
        self.safety_violation_count = 0
        self.window_total_samples = 0
        self.window_open_samples = 0

        self.summary_pub = self.create_publisher(MetricsSummary, "/metrics/summary", 10)

        self.create_subscription(RelativeState, "/relative_state/active", self.relative_state_cb, 10)
        self.create_subscription(MissionStatus, "/mission/phase", self.mission_status_cb, 10)
        self.create_subscription(SafetyStatus, "/safety/status", self.safety_status_cb, 10)
        self.create_subscription(TouchdownState, "/touchdown/state", self.touchdown_state_cb, 10)
        self.create_subscription(ExperimentRunStatus, "/experiment/run_status", self.run_status_cb, 10)
        self.create_subscription(LandingDecisionStatus, "/landing_decision/status", self.decision_status_cb, 10)
        self.create_subscription(LandingWindowStatus, "/landing_window/status", self.window_status_cb, 10)

        self.timer = self.create_timer(1.0, self.maybe_write_summary)
        self.get_logger().info("metrics_evaluator summary writer is running.")

    def relative_state_cb(self, msg):
        self.relative_state = msg
        xy_error = math.hypot(msg.position.x, msg.position.y)
        self.max_xy_error = max(self.max_xy_error, xy_error)
        self.sample_count += 1

    def mission_status_cb(self, msg):
        self.mission_status = msg

    def safety_status_cb(self, msg):
        if self.safety_status is None or (
            not self.safety_status.abort_requested and msg.abort_requested
        ):
            self.safety_violation_count += int(msg.abort_requested)
        self.safety_status = msg

    def touchdown_state_cb(self, msg):
        self.touchdown_state = msg

    def run_status_cb(self, msg):
        self.run_status = msg

    def decision_status_cb(self, msg):
        if (
            msg.advisory == LandingDecisionStatus.GO_AROUND
            and self.last_decision_advisory != LandingDecisionStatus.GO_AROUND
        ):
            self.go_around_count += 1
        self.last_decision_advisory = msg.advisory

    def window_status_cb(self, msg):
        self.window_total_samples += 1
        self.window_open_samples += int(msg.window_open)

    def maybe_write_summary(self):
        if self.summary_written or self.relative_state is None or self.run_status is None:
            return

        mission_complete = (
            self.touchdown_state is not None and self.touchdown_state.landing_completed
        ) or (
            self.mission_status is not None
            and self.mission_status.phase in (MissionStatus.POST_LANDING, MissionStatus.ABORT_GO_AROUND)
        ) or (
            self.safety_status is not None and self.safety_status.abort_requested
        )

        should_write = mission_complete
        if not should_write:
            return

        window_utilization = (
            float(self.window_open_samples) / float(self.window_total_samples)
            if self.window_total_samples
            else 0.0
        )
        touchdown_speed = math.sqrt(
            self.relative_state.linear_velocity.x ** 2
            + self.relative_state.linear_velocity.y ** 2
            + self.relative_state.linear_velocity.z ** 2
        )
        mission_success = bool(
            self.touchdown_state is not None
            and self.touchdown_state.landing_completed
            and not self.touchdown_state.landing_failed
        )
        outcome_label = "success" if mission_success else "aborted_or_failed"

        msg = MetricsSummary()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.mission_success = mission_success
        msg.outcome_label = outcome_label
        msg.terminal_xy_error = math.hypot(self.relative_state.position.x, self.relative_state.position.y)
        msg.terminal_z_error = self.relative_state.position.z
        msg.touchdown_speed = touchdown_speed
        msg.go_around_count = self.go_around_count
        msg.safety_violation_count = self.safety_violation_count
        msg.window_utilization = window_utilization
        self.summary_pub.publish(msg)

        summary = {
            "scenario_id": self.run_status.scenario_id,
            "run_id": self.run_status.run_id,
            "phase": self.mission_status.phase if self.mission_status is not None else -1,
            "safety_reason": self.safety_status.reason if self.safety_status is not None else "unknown",
            "abort_requested": bool(self.safety_status.abort_requested) if self.safety_status else False,
            "landing_completed": bool(self.touchdown_state.landing_completed) if self.touchdown_state else False,
            "landing_failed": bool(self.touchdown_state.landing_failed) if self.touchdown_state else False,
            "outcome_label": outcome_label,
            "max_xy_error_m": self.max_xy_error,
            "final_xy_error_m": msg.terminal_xy_error,
            "final_z_error_m": msg.terminal_z_error,
            "touchdown_speed_mps": touchdown_speed,
            "go_around_count": self.go_around_count,
            "safety_violation_count": self.safety_violation_count,
            "window_utilization": window_utilization,
            "samples": self.sample_count,
            "time_to_event_s": monotonic() - self.start_monotonic,
        }

        if self.run_status.output_dir:
            os.makedirs(self.run_status.output_dir, exist_ok=True)
            with open(os.path.join(self.run_status.output_dir, "summary.json"), "w", encoding="utf-8") as handle:
                json.dump(summary, handle, indent=2, sort_keys=True)

            csv_path = os.path.join(self.run_status.output_dir, "summary.csv")
            with open(csv_path, "w", encoding="utf-8", newline="") as handle:
                writer = csv.DictWriter(handle, fieldnames=list(summary.keys()))
                writer.writeheader()
                writer.writerow(summary)

        self.summary_written = True


def main():
    rclpy.init()
    node = SummaryWriter()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
