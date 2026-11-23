#!/usr/bin/env bash
# Starts the VRX simulation headless together with foxglove_bridge, so I can
# watch the WAM-V from my Mac in Lichtblick (ws://localhost:8765). Run
# scripts/run_viewer.sh next to it. Stop it with Ctrl-C.
#
# To move the boat by hand, from another terminal:
#     docker exec usvviz bash -c "ros2 topic pub -r 10 /wamv/thrusters/left/thrust std_msgs/msg/Float64 '{data: 400.0}'"
#     docker exec usvviz bash -c "ros2 topic pub -r 10 /wamv/thrusters/right/thrust std_msgs/msg/Float64 '{data: 400.0}'"
#
# Usage (from the repo root):
#     scripts/run_sim_viz.sh [world]      # a world in worlds/, default solent_open_water
set -euo pipefail

IMAGE="${IMAGE:-solent-usv-vrx}"
NAME="usvviz"
PORT="${PORT:-8765}"
WORLD="${1:-solent_open_water}"

cleanup() { docker stop "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "Starting VRX headless ($WORLD) + foxglove_bridge..."
docker run -d --rm --name "$NAME" -p "${PORT}:8765" -v "$PWD":/ws "$IMAGE" \
  bash -c "ros2 launch /ws/launch/sim.launch.py world:=$WORLD viz:=true" >/dev/null

echo "Ready. Connect Lichtblick to ws://localhost:${PORT} (Ctrl-C to stop)."
docker logs -f "$NAME" > /dev/null 2>&1 || true
