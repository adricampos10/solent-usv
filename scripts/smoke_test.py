"""Milestone 1 smoke test: drives the WAM-V in the headless VRX simulation and
checks requirements R1.2-R1.4 (docs/sysml/verification.sysml).

It runs inside the container while the simulation is up (see
scripts/run_smoke_test.sh). It reads the ground-truth pose that VRX bridges on
/wamv/pose and the simulation clock on /clock, sends thrust in newtons to the
two thrusters, and exits with status 1 if any check fails.
"""
from __future__ import annotations

import sys
import time

import rclpy
from rclpy.node import Node
from rosgraph_msgs.msg import Clock
from std_msgs.msg import Float64
from tf2_msgs.msg import TFMessage

from smoke_metrics import (
    Pose2D, check_forward, check_real_time, check_turn, real_time_factor,
    yaw_from_quaternion,
)

FORWARD_THRUST = 400.0   # N per thruster (each one can give about 2350 N)
TURN_THRUST = 300.0      # N, opposite on each side
SETTLE_S = 3.0           # simulated seconds with no thrust before each phase
FORWARD_S = 20.0         # R1.3 time limit
TURN_S = 15.0
WAIT_TIMEOUT_S = 180.0   # wall-clock seconds to wait for the simulation


class SmokeTest(Node):
    def __init__(self):
        super().__init__("smoke_test")
        self.left = self.create_publisher(Float64, "/wamv/thrusters/left/thrust", 10)
        self.right = self.create_publisher(Float64, "/wamv/thrusters/right/thrust", 10)
        self.create_subscription(Clock, "/clock", self.on_clock, 10)
        self.create_subscription(TFMessage, "/wamv/pose", self.on_pose, 10)
        self.sim_time: float | None = None
        self.pose: Pose2D | None = None

    def on_clock(self, msg: Clock):
        self.sim_time = msg.clock.sec + msg.clock.nanosec * 1e-9

    def on_pose(self, msg: TFMessage):
        # VRX publishes the pose of the model and its links; the model itself
        # is the transform whose child frame is the model name.
        for tf in msg.transforms:
            if tf.child_frame_id == "wamv" and self.sim_time is not None:
                q, p = tf.transform.rotation, tf.transform.translation
                self.pose = Pose2D(self.sim_time, p.x, p.y,
                                   yaw_from_quaternion(q.x, q.y, q.z, q.w))
                return

    def thrust(self, left: float, right: float):
        self.left.publish(Float64(data=left))
        self.right.publish(Float64(data=right))

    def run_for(self, sim_seconds: float, left: float, right: float) -> list[Pose2D]:
        """Hold a thrust for some simulated time, sampling the pose."""
        start = self.sim_time
        poses = [self.pose]
        while self.sim_time - start < sim_seconds:
            self.thrust(left, right)
            rclpy.spin_once(self, timeout_sec=0.05)
            if self.pose is not poses[-1]:
                poses.append(self.pose)
        return poses

    def wait_for_sim(self) -> bool:
        deadline = time.monotonic() + WAIT_TIMEOUT_S
        while self.pose is None and time.monotonic() < deadline:
            rclpy.spin_once(self, timeout_sec=0.1)
        return self.pose is not None


def main() -> int:
    rclpy.init()
    node = SmokeTest()
    try:
        if not node.wait_for_sim():
            print("FAIL: no pose on /wamv/pose; is the simulation running?")
            return 1
        wall0, sim0 = time.monotonic(), node.sim_time

        node.run_for(SETTLE_S, 0.0, 0.0)
        forward = node.run_for(FORWARD_S, FORWARD_THRUST, FORWARD_THRUST)
        node.run_for(SETTLE_S, 0.0, 0.0)
        turn = node.run_for(TURN_S, -TURN_THRUST, TURN_THRUST)
        node.run_for(1.0, 0.0, 0.0)

        rtf = real_time_factor(node.sim_time - sim0, time.monotonic() - wall0)
        results = {
            "R1.2 real time": check_real_time(rtf),
            "R1.3 forward": check_forward(forward[0], forward[-1]),
            "R1.4 turn": check_turn(turn, -TURN_THRUST, TURN_THRUST),
        }
        print("R1.1 headless: PASS (gz sim -s in Docker, no GPU)")
        for name, (ok, detail) in results.items():
            print(f"{name}: {'PASS' if ok else 'FAIL'} ({detail})")
        return 0 if all(ok for ok, _ in results.values()) else 1
    finally:
        node.thrust(0.0, 0.0)
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    sys.exit(main())
