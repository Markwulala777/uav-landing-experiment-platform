import math

import rclpy
from geometry_msgs.msg import PoseStamped, TwistStamped
from rclpy.node import Node
from std_msgs.msg import Bool, String


class TruthSafetyMonitor(Node):
    def __init__(self):
        super().__init__("truth_safety_monitor")
        self.relative_pose = None
        self.relative_twist = None

        self.declare_parameter("abort_xy_error", 4.0)
        self.declare_parameter("abort_abs_z", 8.0)
        self.declare_parameter("abort_lateral_speed", 3.0)
        self.declare_parameter("descent_xy_gate", 0.75)
        self.declare_parameter("descent_lateral_speed_gate", 0.8)

        self.safe_pub = self.create_publisher(Bool, "/safety_manager/status/safe_to_descend", 10)
        self.abort_pub = self.create_publisher(Bool, "/safety_manager/status/abort_requested", 10)
        self.reason_pub = self.create_publisher(String, "/safety_manager/status/reason", 10)

        self.create_subscription(PoseStamped, "/relative_estimation/truth/relative_pose", self.relative_pose_cb, 10)
        self.create_subscription(TwistStamped, "/relative_estimation/truth/relative_twist", self.relative_twist_cb, 10)
        self.timer = self.create_timer(0.05, self.evaluate)
        self.get_logger().info("safety_manager truth monitor is running.")

    def relative_pose_cb(self, msg):
        self.relative_pose = msg

    def relative_twist_cb(self, msg):
        self.relative_twist = msg

    def evaluate(self):
        if self.relative_pose is None or self.relative_twist is None:
            return

        x = self.relative_pose.pose.position.x
        y = self.relative_pose.pose.position.y
        z = self.relative_pose.pose.position.z
        lateral_speed = math.hypot(self.relative_twist.twist.linear.x, self.relative_twist.twist.linear.y)
        xy_error = math.hypot(x, y)

        abort_xy_error = float(self.get_parameter("abort_xy_error").value)
        abort_abs_z = float(self.get_parameter("abort_abs_z").value)
        abort_lateral_speed = float(self.get_parameter("abort_lateral_speed").value)
        descent_xy_gate = float(self.get_parameter("descent_xy_gate").value)
        descent_lateral_speed_gate = float(self.get_parameter("descent_lateral_speed_gate").value)

        abort_requested = xy_error > abort_xy_error or abs(z) > abort_abs_z or lateral_speed > abort_lateral_speed
        safe_to_descend = xy_error < descent_xy_gate and lateral_speed < descent_lateral_speed_gate and not abort_requested

        reason = "nominal"
        if abort_requested:
            if xy_error > abort_xy_error:
                reason = "abort_xy_error_exceeded"
            elif abs(z) > abort_abs_z:
                reason = "abort_vertical_error_exceeded"
            else:
                reason = "abort_lateral_speed_exceeded"
        elif not safe_to_descend:
            reason = "hold_above_target"

        self.safe_pub.publish(Bool(data=safe_to_descend))
        self.abort_pub.publish(Bool(data=abort_requested))
        self.reason_pub.publish(String(data=reason))


def main():
    rclpy.init()
    node = TruthSafetyMonitor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
