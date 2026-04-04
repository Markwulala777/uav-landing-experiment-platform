# Time Base

This document freezes the current research-baseline time-base policy for the mixed ROS1/ROS2 UAV-USV landing stack.

## Authoritative time source

- Gazebo simulation time is the authoritative time base for shared-world experiments.

## Baseline requirements

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
- Relative-state timestamps on `/relative_state/active`
- Mission-phase transitions on `/mission/phase`
- Landing-window and decision-advisory event timestamps
- Safety-manager state transitions
- Touchdown event timestamps on `/touchdown/event`
- Experiment-manager event log timestamps on `/experiment/events`
- Active control-reference timestamps on `/controller/reference_active`
- PX4 offboard command publication timestamps

## Delay accounting

The current baseline uses truthful low-latency transport and does not yet inject configured delay.
However, the platform must already expose enough timestamps to support later delay instrumentation.

## Acceptance intent

The current baseline is accepted only if:

- ROS2 nodes use simulation time
- run metadata is written per experiment
- summary files can be associated with one replayable run directory
