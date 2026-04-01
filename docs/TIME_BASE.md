# Time Base

This document freezes the Phase 1 time-base policy for the mixed ROS1/ROS2 UAV-USV landing stack.

## Authoritative time source

- Gazebo simulation time is the authoritative time base for shared-world experiments.

## Phase 1 requirements

- ROS1 truth extraction must timestamp messages using simulation-consistent time.
- ROS2 research nodes must run with `use_sim_time=true`.
- PX4 offboard commands must carry timestamps generated from the ROS2 node clock that follows simulation time.
- Experiment metadata must record:
  - `scenario_id`
  - `run_id`
  - `seed`
  - wall-clock creation time
  - output directory

## What must be logged

- Truth deck pose and twist timestamps
- Truth relative pose and twist timestamps
- Landing-guidance phase transitions
- Safety-manager state transitions
- Touchdown event timestamps
- PX4 offboard command publication timestamps

## Delay accounting

Phase 1 uses truthful low-latency transport and does not yet inject configured delay.
However, the platform must already expose enough timestamps to support later delay instrumentation.

## Acceptance intent

Phase 1 is accepted only if:

- ROS2 nodes use simulation time
- run metadata is written per experiment
- summary files can be associated with one replayable run directory
