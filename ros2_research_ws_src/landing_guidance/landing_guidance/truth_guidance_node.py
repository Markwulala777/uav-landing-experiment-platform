import rclpy
from geometry_msgs.msg import PoseStamped
from rclpy.node import Node
from std_msgs.msg import Bool, String


class TruthGuidanceNode(Node):
    def __init__(self):
        super().__init__("truth_guidance")
        self.target_pose = None
        self.uav_pose = None
        self.safe_to_descend = False

        self.declare_parameter("approach_height", 5.0)
        self.declare_parameter("terminal_height", 0.3)
        self.declare_parameter("descent_rate", 0.4)

        self.setpoint_pub = self.create_publisher(PoseStamped, "/landing_guidance/debug/pose_setpoint", 10)
        self.phase_pub = self.create_publisher(String, "/landing_guidance/status/phase", 10)

        self.create_subscription(PoseStamped, "/deck_interface/truth/landing_target_pose", self.target_pose_cb, 10)
        self.create_subscription(PoseStamped, "/deck_interface/truth/uav_pose", self.uav_pose_cb, 10)
        self.create_subscription(Bool, "/safety_manager/status/safe_to_descend", self.safe_to_descend_cb, 10)

        self.commanded_z = None
        self.timer = self.create_timer(0.05, self.publish_setpoint)
        self.get_logger().info("landing_guidance truth node is running.")

    def target_pose_cb(self, msg):
        self.target_pose = msg

    def uav_pose_cb(self, msg):
        self.uav_pose = msg

    def safe_to_descend_cb(self, msg):
        self.safe_to_descend = msg.data

    def publish_setpoint(self):
        if self.target_pose is None or self.uav_pose is None:
            return

        approach_height = float(self.get_parameter("approach_height").value)
        terminal_height = float(self.get_parameter("terminal_height").value)
        descent_rate = float(self.get_parameter("descent_rate").value)

        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = self.target_pose.header.frame_id
        msg.pose.position.x = self.target_pose.pose.position.x
        msg.pose.position.y = self.target_pose.pose.position.y
        msg.pose.orientation = self.target_pose.pose.orientation

        if self.commanded_z is None:
            self.commanded_z = self.uav_pose.pose.position.z

        if not self.safe_to_descend:
            phase = "hold_above_target"
            self.commanded_z = self.target_pose.pose.position.z + approach_height
        else:
            phase = "terminal_descent"
            target_terminal_z = self.target_pose.pose.position.z + terminal_height
            self.commanded_z = max(target_terminal_z, self.commanded_z - descent_rate / 20.0)

        msg.pose.position.z = self.commanded_z

        self.setpoint_pub.publish(msg)
        self.phase_pub.publish(String(data=phase))


def main():
    rclpy.init()
    node = TruthGuidanceNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
