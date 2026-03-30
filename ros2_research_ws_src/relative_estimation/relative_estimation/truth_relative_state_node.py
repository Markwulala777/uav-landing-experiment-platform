import math

import rclpy
from geometry_msgs.msg import PoseStamped, TwistStamped
from rclpy.node import Node


def quat_conjugate(q):
    return [-q[0], -q[1], -q[2], q[3]]


def quat_multiply(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2
    return [
        w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2,
        w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2,
        w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2,
        w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2,
    ]


def rotate_vector(q, vector):
    x, y, z, w = q
    xx, yy, zz = x * x, y * y, z * z
    xy, xz, yz = x * y, x * z, y * z
    wx, wy, wz = w * x, w * y, w * z

    return [
        (1.0 - 2.0 * (yy + zz)) * vector[0] + 2.0 * (xy - wz) * vector[1] + 2.0 * (xz + wy) * vector[2],
        2.0 * (xy + wz) * vector[0] + (1.0 - 2.0 * (xx + zz)) * vector[1] + 2.0 * (yz - wx) * vector[2],
        2.0 * (xz - wy) * vector[0] + 2.0 * (yz + wx) * vector[1] + (1.0 - 2.0 * (xx + yy)) * vector[2],
    ]


class TruthRelativeStateNode(Node):
    def __init__(self):
        super().__init__("truth_relative_state")
        self.target_pose = None
        self.target_twist = None
        self.uav_pose = None
        self.uav_twist = None

        self.relative_pose_pub = self.create_publisher(PoseStamped, "/relative_estimation/truth/relative_pose", 10)
        self.relative_twist_pub = self.create_publisher(TwistStamped, "/relative_estimation/truth/relative_twist", 10)

        self.create_subscription(PoseStamped, "/deck_interface/truth/landing_target_pose", self.target_pose_cb, 10)
        self.create_subscription(TwistStamped, "/deck_interface/truth/landing_target_twist", self.target_twist_cb, 10)
        self.create_subscription(PoseStamped, "/deck_interface/truth/uav_pose", self.uav_pose_cb, 10)
        self.create_subscription(TwistStamped, "/deck_interface/truth/uav_twist", self.uav_twist_cb, 10)

        self.timer = self.create_timer(0.05, self.publish_relative_state)
        self.get_logger().info("relative_estimation truth node is running.")

    def target_pose_cb(self, msg):
        self.target_pose = msg

    def target_twist_cb(self, msg):
        self.target_twist = msg

    def uav_pose_cb(self, msg):
        self.uav_pose = msg

    def uav_twist_cb(self, msg):
        self.uav_twist = msg

    def publish_relative_state(self):
        if not all([self.target_pose, self.target_twist, self.uav_pose, self.uav_twist]):
            return

        target_q = [
            self.target_pose.pose.orientation.x,
            self.target_pose.pose.orientation.y,
            self.target_pose.pose.orientation.z,
            self.target_pose.pose.orientation.w,
        ]
        target_q_inv = quat_conjugate(target_q)
        uav_q = [
            self.uav_pose.pose.orientation.x,
            self.uav_pose.pose.orientation.y,
            self.uav_pose.pose.orientation.z,
            self.uav_pose.pose.orientation.w,
        ]

        relative_position_world = [
            self.uav_pose.pose.position.x - self.target_pose.pose.position.x,
            self.uav_pose.pose.position.y - self.target_pose.pose.position.y,
            self.uav_pose.pose.position.z - self.target_pose.pose.position.z,
        ]
        relative_linear_world = [
            self.uav_twist.twist.linear.x - self.target_twist.twist.linear.x,
            self.uav_twist.twist.linear.y - self.target_twist.twist.linear.y,
            self.uav_twist.twist.linear.z - self.target_twist.twist.linear.z,
        ]
        relative_angular_world = [
            self.uav_twist.twist.angular.x - self.target_twist.twist.angular.x,
            self.uav_twist.twist.angular.y - self.target_twist.twist.angular.y,
            self.uav_twist.twist.angular.z - self.target_twist.twist.angular.z,
        ]

        relative_position_target = rotate_vector(target_q_inv, relative_position_world)
        relative_linear_target = rotate_vector(target_q_inv, relative_linear_world)
        relative_angular_target = rotate_vector(target_q_inv, relative_angular_world)
        relative_q = quat_multiply(target_q_inv, uav_q)

        pose_msg = PoseStamped()
        pose_msg.header.stamp = self.uav_pose.header.stamp
        pose_msg.header.frame_id = "landing_target_frame"
        pose_msg.pose.position.x = relative_position_target[0]
        pose_msg.pose.position.y = relative_position_target[1]
        pose_msg.pose.position.z = relative_position_target[2]
        pose_msg.pose.orientation.x = relative_q[0]
        pose_msg.pose.orientation.y = relative_q[1]
        pose_msg.pose.orientation.z = relative_q[2]
        pose_msg.pose.orientation.w = relative_q[3]

        twist_msg = TwistStamped()
        twist_msg.header.stamp = self.uav_twist.header.stamp
        twist_msg.header.frame_id = "landing_target_frame"
        twist_msg.twist.linear.x = relative_linear_target[0]
        twist_msg.twist.linear.y = relative_linear_target[1]
        twist_msg.twist.linear.z = relative_linear_target[2]
        twist_msg.twist.angular.x = relative_angular_target[0]
        twist_msg.twist.angular.y = relative_angular_target[1]
        twist_msg.twist.angular.z = relative_angular_target[2]

        self.relative_pose_pub.publish(pose_msg)
        self.relative_twist_pub.publish(twist_msg)


def main():
    rclpy.init()
    node = TruthRelativeStateNode()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
