from builtin_interfaces.msg import Duration
import rclpy
from rclpy.node import Node
from uav_usv_landing_msgs.msg import (
    LandingZoneState,
    MissionStatus,
    ReferenceTrajectory,
    ReferenceTrajectoryPoint,
)


class MovingDeckPlannerNode(Node):
    def __init__(self):
        super().__init__("moving_deck_planner")

        self.mission_status = None
        self.zone_state = None

        self.reference_pub = self.create_publisher(
            ReferenceTrajectory, "/planner/reference_trajectory", 10
        )

        self.create_subscription(MissionStatus, "/mission/phase", self.mission_status_cb, 10)
        self.create_subscription(LandingZoneState, "/deck/landing_zone_state", self.zone_state_cb, 10)

        self.timer = self.create_timer(0.1, self.publish_stub)
        self.get_logger().info("trajectory_planner baseline stub is running.")

    def mission_status_cb(self, msg):
        self.mission_status = msg

    def zone_state_cb(self, msg):
        self.zone_state = msg

    def publish_stub(self):
        if self.mission_status is None or self.zone_state is None:
            return

        point = ReferenceTrajectoryPoint()
        point.time_from_start = Duration(sec=0, nanosec=0)
        point.pose = self.zone_state.center_pose

        msg = ReferenceTrajectory()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.phase = self.mission_status.phase
        msg.trajectory_points = [point]
        msg.terminal_spec = "baseline_stub_terminal_point"
        msg.feasible = True
        msg.replan_reason = "baseline_stub"
        msg.source = "trajectory_planner_stub"
        self.reference_pub.publish(msg)


def main():
    rclpy.init()
    node = MovingDeckPlannerNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
