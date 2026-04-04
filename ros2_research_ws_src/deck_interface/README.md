# deck_interface

Owns the public deck-side research interface:

- `/deck/state_truth`
- `/deck/landing_zone_state`

It does not permanently own `/uav/*`. The transitional `uav_truth_provider`
node exists only to keep the current baseline runnable while a dedicated
UAV-state package is not yet extracted.
