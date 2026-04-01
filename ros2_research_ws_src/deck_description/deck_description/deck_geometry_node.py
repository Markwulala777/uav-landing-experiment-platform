from geometry_msgs.msg import Point32, PolygonStamped, PoseStamped
import rclpy
from rclpy.node import Node


class DeckGeometryNode(Node):
    def __init__(self):
        super().__init__("deck_geometry")

        self.declare_parameter("deck_length", 2.0)
        self.declare_parameter("deck_width", 1.2)
        self.declare_parameter("landing_target_x", 0.5)
        self.declare_parameter("landing_target_y", 0.0)
        self.declare_parameter("landing_target_z", 0.0)

        self.contact_zone_pub = self.create_publisher(PolygonStamped, "/deck_description/contact_zone", 10)
        self.target_offset_pub = self.create_publisher(PoseStamped, "/deck_description/landing_target_offset", 10)
        self.timer = self.create_timer(1.0, self.publish_metadata)
        self.get_logger().info("deck_description geometry publisher is running.")

    def publish_metadata(self):
        deck_length = float(self.get_parameter("deck_length").value)
        deck_width = float(self.get_parameter("deck_width").value)
        target_x = float(self.get_parameter("landing_target_x").value)
        target_y = float(self.get_parameter("landing_target_y").value)
        target_z = float(self.get_parameter("landing_target_z").value)

        stamp = self.get_clock().now().to_msg()

        polygon_msg = PolygonStamped()
        polygon_msg.header.stamp = stamp
        polygon_msg.header.frame_id = "deck_frame"
        half_length = deck_length / 2.0
        half_width = deck_width / 2.0
        polygon_msg.polygon.points = [
            Point32(x=half_length, y=half_width, z=0.0),
            Point32(x=half_length, y=-half_width, z=0.0),
            Point32(x=-half_length, y=-half_width, z=0.0),
            Point32(x=-half_length, y=half_width, z=0.0),
        ]

        target_msg = PoseStamped()
        target_msg.header.stamp = stamp
        target_msg.header.frame_id = "deck_frame"
        target_msg.pose.position.x = target_x
        target_msg.pose.position.y = target_y
        target_msg.pose.position.z = target_z
        target_msg.pose.orientation.w = 1.0

        self.contact_zone_pub.publish(polygon_msg)
        self.target_offset_pub.publish(target_msg)


def main():
    rclpy.init()
    node = DeckGeometryNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
