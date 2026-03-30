from functools import partial

import rclpy
from geometry_msgs.msg import PoseStamped, TwistStamped
from rclpy.node import Node


class DeckTruthRelay(Node):
    def __init__(self):
        super().__init__("deck_truth_relay")
        self.publishers_ = []
        self.subscriptions_ = []

        topic_specs = [
            (PoseStamped, "/bridge/deck/truth/pose", "/deck_interface/truth/deck_pose"),
            (TwistStamped, "/bridge/deck/truth/twist", "/deck_interface/truth/deck_twist"),
            (PoseStamped, "/bridge/landing_target/truth/pose", "/deck_interface/truth/landing_target_pose"),
            (TwistStamped, "/bridge/landing_target/truth/twist", "/deck_interface/truth/landing_target_twist"),
            (PoseStamped, "/bridge/uav/truth/pose", "/deck_interface/truth/uav_pose"),
            (TwistStamped, "/bridge/uav/truth/twist", "/deck_interface/truth/uav_twist"),
            (PoseStamped, "/bridge/relative/truth/pose", "/deck_interface/truth/relative_pose_bridge"),
            (TwistStamped, "/bridge/relative/truth/twist", "/deck_interface/truth/relative_twist_bridge"),
        ]

        for msg_type, source_topic, target_topic in topic_specs:
            publisher = self.create_publisher(msg_type, target_topic, 10)
            subscription = self.create_subscription(
                msg_type,
                source_topic,
                partial(self.forward_message, publisher),
                10,
            )
            self.publishers_.append(publisher)
            self.subscriptions_.append(subscription)

        self.get_logger().info("deck_interface relay is running.")

    def forward_message(self, publisher, message):
        publisher.publish(message)


def main():
    rclpy.init()
    node = DeckTruthRelay()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
