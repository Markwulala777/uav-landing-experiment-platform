# Phase 1 Acceptance Checklist

Phase 1 is intended to validate the shared-world truth-level landing baseline, not the full doctoral platform.

## Required acceptance items

- One shared Gazebo world only
- ROS2 research nodes run with `use_sim_time=true`
- Truth deck and relative-state interfaces are available
- The frame convention is frozen and the ENU-to-NED conversion happens exactly once in `landing_guidance/px4_offboard_bridge`
- Frame audit passes with configured tolerances
- ROS2 guidance owns the UAV outer loop through PX4 offboard topics
- Pre-touchdown corridor hold is measurable
- Touchdown outcomes are labeled
- Per-run metadata and summary metrics are written to disk
- Calm and moderate scenarios are both representable through configuration

## Phase 1 deliverables in this repository

- `deck_interface_ros1`
- `deck_interface`
- `relative_estimation`
- `landing_guidance`
- `safety_manager`
- `touchdown_manager`
- `deck_description`
- `frame_audit`
- `experiment_manager`
- `metrics_evaluator`
- `joint_bringup`
