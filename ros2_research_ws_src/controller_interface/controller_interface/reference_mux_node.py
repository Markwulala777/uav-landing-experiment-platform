from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from uav_usv_landing_msgs.msg import (
    ControllerReference,
    GuidanceReference,
    ReferenceTrajectory,
)


class ReferenceMuxNode(Node):
    def __init__(self):
        super().__init__("reference_mux")

        self.guidance_reference = None
        self.trajectory_reference = None

        self.declare_parameter("source_mode", "guidance")

        self.reference_pub = self.create_publisher(
            ControllerReference, "/controller/reference_active", 10
        )

        self.create_subscription(GuidanceReference, "/guidance/reference", self.guidance_cb, 10)
        self.create_subscription(
            ReferenceTrajectory, "/planner/reference_trajectory", self.trajectory_cb, 10
        )

        self.timer = self.create_timer(0.05, self.publish_reference)
        self.get_logger().info("controller_interface reference mux is running.")

    def guidance_cb(self, msg):
        self.guidance_reference = msg

    def trajectory_cb(self, msg):
        self.trajectory_reference = msg

    def publish_reference(self):
        preferred_source = str(self.get_parameter("source_mode").value).strip().lower()

        if preferred_source == "planner" and self.trajectory_reference is not None:
            msg = ControllerReference()
            msg.header.stamp = self.get_clock().now().to_msg()
            msg.source_type = ControllerReference.SOURCE_TRAJECTORY
            msg.phase = self.trajectory_reference.phase
            if self.trajectory_reference.trajectory_points:
                first_point = self.trajectory_reference.trajectory_points[0]
                msg.target_pose = first_point.pose
                msg.target_twist = first_point.twist
            else:
                msg.target_twist = Twist()
            msg.terminal_spec = self.trajectory_reference.terminal_spec
            msg.feasible = self.trajectory_reference.feasible
            msg.source = self.trajectory_reference.source
            self.reference_pub.publish(msg)
            return

        if self.guidance_reference is None:
            return

        msg = ControllerReference()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.source_type = ControllerReference.SOURCE_GUIDANCE
        msg.phase = self.guidance_reference.phase
        msg.target_pose = self.guidance_reference.target_pose
        msg.target_twist.linear.x = self.guidance_reference.target_velocity_envelope.x
        msg.target_twist.linear.y = self.guidance_reference.target_velocity_envelope.y
        msg.target_twist.linear.z = self.guidance_reference.target_velocity_envelope.z
        msg.terminal_spec = "guidance_reference"
        msg.feasible = True
        msg.source = self.guidance_reference.source
        self.reference_pub.publish(msg)


def main():
    rclpy.init()
    node = ReferenceMuxNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
