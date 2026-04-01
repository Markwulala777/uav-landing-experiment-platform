from datetime import datetime
import json
import os

import rclpy
from rclpy.node import Node
from std_msgs.msg import Int32, String


class ScenarioRunner(Node):
    def __init__(self):
        super().__init__("experiment_manager")

        self.declare_parameter("scenario_id", "calm_truth")
        self.declare_parameter("run_id", "")
        self.declare_parameter("seed", 42)
        self.declare_parameter("sea_state", "calm")
        self.declare_parameter("controller_variant", "truth_guidance_px4")
        self.declare_parameter("delay_profile", "none")
        self.declare_parameter("output_root", os.path.expanduser("~/uav-usv-experiment-runs"))

        self.scenario_id = str(self.get_parameter("scenario_id").value)
        self.run_id = str(self.get_parameter("run_id").value) or datetime.now().strftime("%Y%m%d_%H%M%S")
        self.seed = int(self.get_parameter("seed").value)
        self.sea_state = str(self.get_parameter("sea_state").value)
        self.controller_variant = str(self.get_parameter("controller_variant").value)
        self.delay_profile = str(self.get_parameter("delay_profile").value)
        self.output_root = os.path.expanduser(str(self.get_parameter("output_root").value))
        self.output_dir = os.path.join(self.output_root, self.scenario_id, self.run_id)

        self.scenario_pub = self.create_publisher(String, "/experiment_manager/scenario_id", 10)
        self.run_id_pub = self.create_publisher(String, "/experiment_manager/run_id", 10)
        self.output_dir_pub = self.create_publisher(String, "/experiment_manager/output_dir", 10)
        self.event_pub = self.create_publisher(String, "/experiment_manager/event", 10)
        self.seed_pub = self.create_publisher(Int32, "/experiment_manager/seed", 10)

        self.prepare_output_dir()
        self.timer = self.create_timer(1.0, self.publish_metadata)
        self.get_logger().info(
            f"experiment_manager is running. scenario_id={self.scenario_id}, run_id={self.run_id}, output_dir={self.output_dir}"
        )

    def prepare_output_dir(self):
        os.makedirs(self.output_dir, exist_ok=True)

        metadata = {
            "scenario_id": self.scenario_id,
            "run_id": self.run_id,
            "seed": self.seed,
            "sea_state": self.sea_state,
            "controller_variant": self.controller_variant,
            "delay_profile": self.delay_profile,
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
                f"sea_state: {self.sea_state}",
                f"controller_variant: {self.controller_variant}",
                f"delay_profile: {self.delay_profile}",
                f"output_dir: {self.output_dir}",
            ]
        )
        with open(os.path.join(self.output_dir, "scenario.yaml"), "w", encoding="utf-8") as handle:
            handle.write(scenario_yaml + "\n")

    def publish_metadata(self):
        self.scenario_pub.publish(String(data=self.scenario_id))
        self.run_id_pub.publish(String(data=self.run_id))
        self.output_dir_pub.publish(String(data=self.output_dir))
        self.event_pub.publish(String(data="running"))
        self.seed_pub.publish(Int32(data=self.seed))


def main():
    rclpy.init()
    node = ScenarioRunner()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
