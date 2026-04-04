import rclpy
from geometry_msgs.msg import PoseStamped, TwistStamped
from rclpy.node import Node
from uav_usv_landing_msgs.msg import DeckState


class DeckTruthIngestNode(Node):
    def __init__(self):
        super().__init__("deck_truth_ingest")

        self.deck_pose = None
        self.deck_twist = None

        self.declare_parameter("deck_source", "ros1_bridge_truth")

        self.deck_state_pub = self.create_publisher(DeckState, "/deck/state_truth", 10)
        self.deck_pose_debug_pub = self.create_publisher(PoseStamped, "/deck_interface/truth/deck_pose", 10)
        self.deck_twist_debug_pub = self.create_publisher(TwistStamped, "/deck_interface/truth/deck_twist", 10)

        self.create_subscription(PoseStamped, "/bridge/deck/truth/pose", self.deck_pose_cb, 10)
        self.create_subscription(TwistStamped, "/bridge/deck/truth/twist", self.deck_twist_cb, 10)
        self.timer = self.create_timer(0.05, self.publish_outputs)
        self.get_logger().info("deck_interface deck truth ingest is running.")

    def deck_pose_cb(self, msg):
        self.deck_pose = msg
        self.deck_pose_debug_pub.publish(msg)

    def deck_twist_cb(self, msg):
        self.deck_twist = msg
        self.deck_twist_debug_pub.publish(msg)

    def publish_outputs(self):
        if self.deck_pose is None or self.deck_twist is None:
            return

        msg = DeckState()
        msg.header = self.deck_pose.header
        msg.pose = self.deck_pose.pose
        msg.twist = self.deck_twist.twist
        msg.angular_velocity = self.deck_twist.twist.angular
        msg.source = str(self.get_parameter("deck_source").value)
        self.deck_state_pub.publish(msg)


def main():
    rclpy.init()
    node = DeckTruthIngestNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
