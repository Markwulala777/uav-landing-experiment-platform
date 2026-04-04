from datetime import datetime
import json
import os

import rclpy
from rclpy.node import Node
from uav_usv_landing_msgs.msg import (
    ExperimentEvent,
    ExperimentRunStatus,
    LandingDecisionStatus,
    LandingWindowStatus,
    MissionStatus,
    SafetyStatus,
    TouchdownEvent,
)


class ScenarioRunner(Node):
    def __init__(self):
        super().__init__("experiment_manager")

        self.declare_parameter("scenario_id", "calm_truth")
        self.declare_parameter("run_id", "")
        self.declare_parameter("seed", 42)
        self.declare_parameter("mode", "baseline_minimal")
        self.declare_parameter("output_root", os.path.expanduser("~/uav-usv-experiment-runs"))

        self.scenario_id = str(self.get_parameter("scenario_id").value)
        self.run_id = str(self.get_parameter("run_id").value) or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.seed = int(self.get_parameter("seed").value)
        self.mode = str(self.get_parameter("mode").value)
        self.output_root = os.path.expanduser(str(self.get_parameter("output_root").value))
        self.output_dir = ""
        self.current_phase = MissionStatus.SEARCH
        self.last_phase = None
        self.last_window_signature = None
        self.last_decision_signature = None
        self.last_safety_signature = None

        self.run_status_pub = self.create_publisher(ExperimentRunStatus, "/experiment/run_status", 10)
        self.event_pub = self.create_publisher(ExperimentEvent, "/experiment/events", 10)

        self.prepare_output_dir()

        self.create_subscription(MissionStatus, "/mission/phase", self.phase_cb, 10)
        self.create_subscription(LandingWindowStatus, "/landing_window/status", self.window_cb, 10)
        self.create_subscription(LandingDecisionStatus, "/landing_decision/status", self.decision_cb, 10)
        self.create_subscription(SafetyStatus, "/safety/status", self.safety_cb, 10)
        self.create_subscription(TouchdownEvent, "/touchdown/event", self.touchdown_event_cb, 10)

        self.timer = self.create_timer(1.0, self.publish_metadata)
        self.emit_event("experiment_manager", "run", "run_started", "experiment run started")
        self.get_logger().info(
            f"experiment_manager is running. scenario_id={self.scenario_id}, run_id={self.run_id}, output_dir={self.output_dir}"
        )

    def prepare_output_dir(self):
        if not self.output_root:
            self.output_dir = ""
            return

        self.output_dir = os.path.join(self.output_root, self.scenario_id, self.run_id)
        os.makedirs(self.output_dir, exist_ok=True)

        metadata = {
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "seed": self.seed,
            "mode": self.mode,
            "created_at": datetime.now().isoformat(),
            "output_dir": self.output_dir,
        }

        with open(os.path.join(self.output_dir, "run_metadata.json"), "w", encoding="utf-8") as handle:
            json.dump(metadata, handle, indent=2, sort_keys=True)

        scenario_yaml = "\n".join(
            [
                f"scenario_id: {self.scenario_id}",
                f"run_id: {self.run_id}",
                f"seed: {self.seed}",
                f"mode: {self.mode}",
                f"output_dir: {self.output_dir}",
            ]
        )
        with open(os.path.join(self.output_dir, "scenario.yaml"), "w", encoding="utf-8") as handle:
            handle.write(scenario_yaml + "\n")

    def append_event_record(self, record):
        if not self.output_dir:
            return

        with open(os.path.join(self.output_dir, "events.jsonl"), "a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, sort_keys=True) + "\n")

    def emit_event(self, source_pkg, event_type, code, text):
        msg = ExperimentEvent()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.source_pkg = source_pkg
        msg.event_type = event_type
        msg.code = code
        msg.phase = self.current_phase
        msg.text = text
        self.event_pub.publish(msg)
        self.append_event_record(
            {
                "stamp": {"sec": msg.header.stamp.sec, "nanosec": msg.header.stamp.nanosec},
                "source_pkg": source_pkg,
                "event_type": event_type,
                "code": code,
                "phase": int(self.current_phase),
                "text": text,
            }
        )

    def phase_cb(self, msg):
        self.current_phase = msg.phase
        if self.last_phase != msg.phase:
            self.last_phase = msg.phase
            self.emit_event("mission_manager", "mission_phase", str(msg.phase), msg.transition_reason)

    def window_cb(self, msg):
        signature = (bool(msg.window_open), str(msg.window_reason))
        if signature != self.last_window_signature:
            self.last_window_signature = signature
            code = "window_open" if msg.window_open else "window_closed"
            self.emit_event("landing_decision", "landing_window", code, msg.window_reason)

    def decision_cb(self, msg):
        signature = (int(msg.advisory), tuple(msg.reason_codes))
        if signature != self.last_decision_signature:
            self.last_decision_signature = signature
            self.emit_event(
                "landing_decision",
                "decision_advisory",
                str(msg.advisory),
                ",".join(msg.reason_codes),
            )

    def safety_cb(self, msg):
        signature = (bool(msg.abort_requested), str(msg.reason))
        if signature != self.last_safety_signature:
            self.last_safety_signature = signature
            self.emit_event("safety_manager", "safety_status", msg.reason, msg.reason)

    def touchdown_event_cb(self, msg):
        self.emit_event("touchdown_manager", "touchdown_event", msg.event_type, msg.reason)

    def publish_metadata(self):
        msg = ExperimentRunStatus()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.scenario_id = self.scenario_id
        msg.run_id = self.run_id
        msg.seed = self.seed
        msg.output_dir = self.output_dir
        msg.mode = self.mode
        msg.state = "running"
        self.run_status_pub.publish(msg)


def main():
    rclpy.init()
    node = ScenarioRunner()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
