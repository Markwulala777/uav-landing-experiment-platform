# safety_manager

Owns `/safety/status` and `/safety/abort_request`.

It may filter a controller reference onto `/controller/reference_filtered`, but
it does not publish final PX4/offboard commands.
