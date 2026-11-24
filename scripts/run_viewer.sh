#!/usr/bin/env bash
# Starts the Lichtblick web viewer (open-source Foxglove) with my layout: the
# boat in 3D, its GNSS position on a map of the Solent, yaw rate and thrust.
# Run it next to
# scripts/run_sim_viz.sh and open the URL it prints. Stop it with Ctrl-C.
#
# Usage (from the repo root):
#     scripts/run_viewer.sh
set -euo pipefail

VIEWER_IMAGE="${VIEWER_IMAGE:-ghcr.io/lichtblick-suite/lichtblick:latest}"

echo "Open http://localhost:8080/?ds=foxglove-websocket&ds.url=ws://localhost:8765"
docker run --rm --name lichtblick -p 8080:8080 \
  -v "$PWD/viz/lichtblick_layout.json":/lichtblick/default-layout.json:ro \
  "$VIEWER_IMAGE"
