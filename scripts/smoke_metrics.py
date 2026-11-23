"""Pure-Python checks for the milestone 1 smoke test (no ROS imports).

They take poses sampled from the simulation and decide whether requirements
R1.2-R1.4 in docs/sysml/verification.sysml are met, so I can unit-test the
checks without running Gazebo.
"""
from __future__ import annotations

import math
from dataclasses import dataclass


@dataclass(frozen=True)
class Pose2D:
    """Boat pose in the world frame: position in metres, heading in radians."""
    t: float      # simulation time, s
    x: float
    y: float
    yaw: float


def yaw_from_quaternion(qx: float, qy: float, qz: float, qw: float) -> float:
    """Heading (rotation about z) from a unit quaternion, in [-pi, pi]."""
    return math.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))


def wrap_angle(a: float) -> float:
    """Wrap an angle to [-pi, pi)."""
    return (a + math.pi) % (2.0 * math.pi) - math.pi


def real_time_factor(sim_elapsed: float, wall_elapsed: float) -> float:
    """Simulated seconds per wall-clock second (R1.2)."""
    if wall_elapsed <= 0.0:
        raise ValueError("wall_elapsed must be positive")
    return sim_elapsed / wall_elapsed


def forward_distance(start: Pose2D, end: Pose2D) -> float:
    """Displacement along the boat's starting heading (R1.3).

    Positive when the boat moved bow-first; sideways drift doesn't count.
    """
    dx, dy = end.x - start.x, end.y - start.y
    return dx * math.cos(start.yaw) + dy * math.sin(start.yaw)


def mean_yaw_rate(poses: list[Pose2D]) -> float:
    """Average yaw rate over a run, in rad/s, counter-clockwise positive (R1.4).

    It adds up wrapped heading changes, so it is correct across the +-pi seam.
    """
    if len(poses) < 2:
        raise ValueError("need at least two poses")
    turned = sum(wrap_angle(b.yaw - a.yaw) for a, b in zip(poses, poses[1:]))
    duration = poses[-1].t - poses[0].t
    if duration <= 0.0:
        raise ValueError("poses must span a positive time")
    return turned / duration


def max_displacement(poses: list[Pose2D]) -> float:
    """Largest distance from the first pose: how far a turn 'on the spot' wandered."""
    x0, y0 = poses[0].x, poses[0].y
    return max(math.hypot(p.x - x0, p.y - y0) for p in poses)


def check_forward(start: Pose2D, end: Pose2D, min_distance: float = 5.0,
                  time_limit: float = 20.0) -> tuple[bool, str]:
    """R1.3: equal positive thrust moves the boat forward >= min_distance within time_limit."""
    d = forward_distance(start, end)
    elapsed = end.t - start.t
    ok = d >= min_distance and elapsed <= time_limit + 1e-6
    return ok, f"forward {d:.1f} m in {elapsed:.1f} s (need >= {min_distance} m in <= {time_limit} s)"


def check_turn(poses: list[Pose2D], left_thrust: float, right_thrust: float,
               min_rate: float = math.radians(2.0)) -> tuple[bool, str]:
    """R1.4: opposite thrust turns the boat towards the side with the weaker thruster.

    More thrust on the right (starboard) hull pushes the bow to port, so the boat
    turns counter-clockwise (positive yaw rate). min_rate rejects noise.
    """
    rate = mean_yaw_rate(poses)
    expected_sign = 1.0 if right_thrust > left_thrust else -1.0
    ok = rate * expected_sign >= min_rate
    return ok, (f"yaw rate {math.degrees(rate):+.1f} deg/s "
                f"(need {'+' if expected_sign > 0 else '-'}{math.degrees(min_rate):.0f} deg/s or more), "
                f"wandered {max_displacement(poses):.1f} m")


def check_real_time(rtf: float, minimum: float = 0.5) -> tuple[bool, str]:
    """R1.2: the simulation runs at a real-time factor of at least `minimum`."""
    return rtf >= minimum, f"real-time factor {rtf:.2f} (need >= {minimum})"
