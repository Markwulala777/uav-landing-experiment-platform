import math

import rclpy
from geometry_msgs.msg import PoseStamped, TwistStamped
from rclpy.node import Node
from std_msgs.msg import Bool, String


class TruthTouchdownMonitor(Node):
    def __init__(self):
        super().__init__("truth_touchdown_monitor")
        self.relative_pose = None
        self.relative_twist = None
        self.touchdown_latched = False

        self.declare_parameter("contact_height_threshold", 0.15)
        self.declare_parameter("success_xy_threshold", 0.5)
        self.declare_parameter("success_vertical_speed", 0.8)
        self.declare_parameter("success_lateral_speed", 0.8)

        self.detected_pub = self.create_publisher(Bool, "/touchdown_manager/status/touchdown_detected", 10)
        self.label_pub = self.create_publisher(String, "/touchdown_manager/status/outcome_label", 10)

        self.create_subscription(PoseStamped, "/relative_estimation/truth/relative_pose", self.relative_pose_cb, 10)
        self.create_subscription(TwistStamped, "/relative_estimation/truth/relative_twist", self.relative_twist_cb, 10)
        self.timer = self.create_timer(0.05, self.evaluate)
        self.get_logger().info("touchdown_manager truth monitor is running.")

    def relative_pose_cb(self, msg):
        self.relative_pose = msg

    def relative_twist_cb(self, msg):
        self.relative_twist = msg

    def evaluate(self):
        if self.relative_pose is None or self.relative_twist is None:
            return

        contact_height_threshold = float(self.get_parameter("contact_height_threshold").value)
        success_xy_threshold = float(self.get_parameter("success_xy_threshold").value)
        success_vertical_speed = float(self.get_parameter("success_vertical_speed").value)
        success_lateral_speed = float(self.get_parameter("success_lateral_speed").value)

        x = self.relative_pose.pose.position.x
        y = self.relative_pose.pose.position.y
        z = self.relative_pose.pose.position.z
        lateral_error = math.hypot(x, y)
        lateral_speed = math.hypot(self.relative_twist.twist.linear.x, self.relative_twist.twist.linear.y)
        vertical_speed = abs(self.relative_twist.twist.linear.z)

        if self.touchdown_latched:
            self.detected_pub.publish(Bool(data=True))
            return

        if z > contact_height_threshold:
            self.detected_pub.publish(Bool(data=False))
            return

        if lateral_error <= success_xy_threshold and lateral_speed <= success_lateral_speed and vertical_speed <= success_vertical_speed:
            label = "success"
        elif lateral_error > success_xy_threshold:
            label = "slide"
        elif vertical_speed > success_vertical_speed:
            label = "bounce"
        else:
            label = "failure"

        self.touchdown_latched = True
        self.detected_pub.publish(Bool(data=True))
        self.label_pub.publish(String(data=label))


def main():
    rclpy.init()
    node = TruthTouchdownMonitor()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
