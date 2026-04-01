import math

from geometry_msgs.msg import PoseStamped
from px4_msgs.msg import OffboardControlMode, TrajectorySetpoint, VehicleCommand
import rclpy
from rclpy.node import Node
from std_msgs.msg import Bool, String


def yaw_from_quaternion(quaternion):
    x = quaternion.x
    y = quaternion.y
    z = quaternion.z
    w = quaternion.w
    siny_cosp = 2.0 * (w * z + x * y)
    cosy_cosp = 1.0 - 2.0 * (y * y + z * z)
    return math.atan2(siny_cosp, cosy_cosp)


def enu_position_to_ned(position):
    return [position.y, position.x, -position.z]


def enu_yaw_to_ned(yaw_enu):
    return math.pi / 2.0 - yaw_enu


class Px4OffboardBridge(Node):
    def __init__(self):
        super().__init__("px4_offboard_bridge")
        self.setpoint = None
        self.abort_requested = False
        self.phase = "initializing"
        self.setpoint_counter = 0
        self.offboard_requested = False
        self.arm_requested = False
        self.abort_command_sent = False

        self.declare_parameter("fmu_prefix", "/fmu")
        self.declare_parameter("publish_rate_hz", 20.0)
        self.declare_parameter("warmup_setpoints", 20)
        self.declare_parameter("auto_arm", True)
        self.declare_parameter("auto_offboard", True)

        fmu_prefix = str(self.get_parameter("fmu_prefix").value).rstrip("/")
        publish_rate_hz = float(self.get_parameter("publish_rate_hz").value)

        self.offboard_mode_pub = self.create_publisher(
            OffboardControlMode, f"{fmu_prefix}/in/offboard_control_mode", 10
        )
        self.trajectory_setpoint_pub = self.create_publisher(
            TrajectorySetpoint, f"{fmu_prefix}/in/trajectory_setpoint", 10
        )
        self.vehicle_command_pub = self.create_publisher(
            VehicleCommand, f"{fmu_prefix}/in/vehicle_command", 10
        )
        self.status_pub = self.create_publisher(String, "/landing_guidance/status/control_owner", 10)

        self.create_subscription(PoseStamped, "/landing_guidance/setpoint/world", self.setpoint_cb, 10)
        self.create_subscription(Bool, "/safety_manager/status/abort_requested", self.abort_requested_cb, 10)
        self.create_subscription(String, "/landing_guidance/status/phase", self.phase_cb, 10)

        self.timer = self.create_timer(1.0 / publish_rate_hz, self.publish_cycle)
        self.get_logger().info("landing_guidance PX4 offboard bridge is running.")

    def setpoint_cb(self, msg):
        self.setpoint = msg

    def abort_requested_cb(self, msg):
        self.abort_requested = msg.data

    def phase_cb(self, msg):
        self.phase = msg.data

    def now_us(self):
        return int(self.get_clock().now().nanoseconds / 1000)

    def publish_vehicle_command(self, command, param1=0.0, param2=0.0):
        msg = VehicleCommand()
        msg.timestamp = self.now_us()
        msg.param1 = float(param1)
        msg.param2 = float(param2)
        msg.command = command
        msg.target_system = 1
        msg.target_component = 1
        msg.source_system = 1
        msg.source_component = 1
        msg.from_external = True
        self.vehicle_command_pub.publish(msg)

    def publish_cycle(self):
        if self.setpoint is None:
            self.status_pub.publish(String(data="waiting_for_guidance_setpoint"))
            return

        timestamp = self.now_us()
        yaw_enu = yaw_from_quaternion(self.setpoint.pose.orientation)
        position_ned = enu_position_to_ned(self.setpoint.pose.position)
        yaw_ned = enu_yaw_to_ned(yaw_enu)

        offboard_msg = OffboardControlMode()
        offboard_msg.timestamp = timestamp
        offboard_msg.position = True
        offboard_msg.velocity = False
        offboard_msg.acceleration = False
        offboard_msg.attitude = False
        offboard_msg.body_rate = False

        trajectory_msg = TrajectorySetpoint()
        trajectory_msg.timestamp = timestamp
        trajectory_msg.position = position_ned
        trajectory_msg.velocity = [math.nan, math.nan, math.nan]
        trajectory_msg.acceleration = [math.nan, math.nan, math.nan]
        trajectory_msg.yaw = float(yaw_ned)

        self.offboard_mode_pub.publish(offboard_msg)
        self.trajectory_setpoint_pub.publish(trajectory_msg)
        self.setpoint_counter += 1

        warmup_setpoints = int(self.get_parameter("warmup_setpoints").value)
        auto_offboard = bool(self.get_parameter("auto_offboard").value)
        auto_arm = bool(self.get_parameter("auto_arm").value)

        if auto_offboard and not self.offboard_requested and self.setpoint_counter >= warmup_setpoints:
            self.publish_vehicle_command(
                VehicleCommand.VEHICLE_CMD_DO_SET_MODE,
                param1=1.0,
                param2=6.0,
            )
            self.offboard_requested = True

        if auto_arm and self.offboard_requested and not self.arm_requested:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_COMPONENT_ARM_DISARM, param1=1.0)
            self.arm_requested = True

        if self.abort_requested and not self.abort_command_sent:
            self.publish_vehicle_command(VehicleCommand.VEHICLE_CMD_NAV_LAND)
            self.abort_command_sent = True

        owner = "ros2_guidance_offboard"
        if self.abort_requested:
            owner = "ros2_guidance_abort_land"
        self.status_pub.publish(String(data=f"{owner}:{self.phase}"))


def main():
    rclpy.init()
    node = Px4OffboardBridge()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()
