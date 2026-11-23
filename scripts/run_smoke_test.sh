#!/usr/bin/env bash
# Milestone 1 smoke test: starts the VRX simulation headless in Docker, drives
# the WAM-V forward and then turns it on the spot, and checks R1.1-R1.4.
# Exits with status 1 if any check fails, so it can run in CI.
#
# Usage (from the repo root, after building the image):
#     docker build -t solent-usv-vrx docker/vrx
#     scripts/run_smoke_test.sh [world]      # a world in worlds/, default solent_open_water
set -euo pipefail

IMAGE="${IMAGE:-solent-usv-vrx}"
WORLD="${1:-solent_open_water}"
NAME="usv-smoke-$$"

cleanup() { docker stop "$NAME" >/dev/null 2>&1 || true; }
trap cleanup EXIT

echo "Starting VRX headless ($WORLD)..."
docker run -d --rm --name "$NAME" -v "$PWD":/ws "$IMAGE" \
  bash -c "ros2 launch /ws/launch/sim.launch.py world:=$WORLD" >/dev/null

echo "Running the unit tests..."
docker exec "$NAME" bash -c "python3 -m pytest -q"

echo "Running the smoke test..."
docker exec "$NAME" bash -c "python3 /ws/scripts/smoke_test.py"
