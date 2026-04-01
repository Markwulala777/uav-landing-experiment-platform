# Frame Convention

This document freezes the Phase 1 frame convention for the mixed ROS1/ROS2 UAV-USV landing stack.

## Goals

- Use one shared Gazebo world frame for truth-level logging and replay.
- Make ENU-to-NED conversion explicit and perform it exactly once.
- Keep deck-relative states reproducible across ROS1, ROS2, and PX4.

## Canonical frames

- `world`
  - Gazebo shared world frame.
  - Convention: ENU.
  - Used for truth logging, deck truth, and scenario-level metrics.
- `wamv/base_link`
  - Body frame attached to the WAM-V carrier.
  - Used for carrier pose, velocity, and angular-rate interpretation.
- `deck_frame`
  - Deck-fixed frame attached to the landing surface.
  - Used for deck geometry and contact-zone definitions.
- `landing_target_frame`
  - Deck-fixed target frame at the nominal touchdown point.
  - Used for terminal guidance and touchdown evaluation.
- `uav/base_link`
  - UAV body frame.
  - Used for flight-state interpretation and future estimator outputs.
- `camera_*`
  - Onboard sensing frames attached to the UAV camera chain.
  - Reserved for Phase 2 perception-only experiments.

## Truth publishing responsibilities

- ROS1 `deck_interface_ros1`
  - Publishes deck truth, target truth, UAV truth, and truth relative states.
  - Source topics come from `/gazebo/model_states`.
- ROS2 `deck_interface`
  - Relays ROS1 bridge truth topics into the Phase 1 research namespace.
- ROS2 `relative_estimation`
  - Recomputes truth relative states independently for auditability.

## Relative-state convention

- Relative position is defined as:
  - `uav_position - landing_target_position`
- Truth-level relative position and velocity are expressed in `landing_target_frame`.
- Touchdown classification uses deck-relative states, not world-frame proximity alone.

## ENU to NED conversion

The only allowed ENU-to-NED conversion point in Phase 1 is:

- ROS2 `landing_guidance.px4_offboard_bridge`

Conversion rules:

- Position:
  - `x_ned = y_enu`
  - `y_ned = x_enu`
  - `z_ned = -z_enu`
- Yaw:
  - `yaw_ned = pi/2 - yaw_enu`

No other node may silently convert the same state again.

## Audit rules

The Phase 1 `frame_audit` node checks:

- Target offset consistency between `deck_frame` and `landing_target_frame`
- Relative position consistency between world-frame truth and target-frame truth
- Relative velocity consistency between world-frame truth and target-frame truth

Phase 1 is not accepted unless the audit remains within the configured tolerances.
