import math

import pytest

from smoke_metrics import (
    Pose2D, check_forward, check_real_time, check_turn, forward_distance,
    mean_yaw_rate, real_time_factor, wrap_angle, yaw_from_quaternion,
)


def test_yaw_from_quaternion():
    half = math.radians(90) / 2
    assert yaw_from_quaternion(0, 0, math.sin(half), math.cos(half)) == pytest.approx(math.pi / 2)
    assert yaw_from_quaternion(0, 0, 0, 1) == pytest.approx(0.0)


def test_wrap_angle():
    assert wrap_angle(3 * math.pi / 2) == pytest.approx(-math.pi / 2)
    assert wrap_angle(-3 * math.pi / 2) == pytest.approx(math.pi / 2)


def test_forward_distance_follows_start_heading():
    start = Pose2D(0, 0, 0, math.pi / 2)       # bow pointing north (+y)
    assert forward_distance(start, Pose2D(10, 0, 8, 0)) == pytest.approx(8)
    assert forward_distance(start, Pose2D(10, 8, 0, 0)) == pytest.approx(0)   # pure sideways drift
    assert forward_distance(start, Pose2D(10, 0, -3, 0)) == pytest.approx(-3)  # went astern


def test_check_forward():
    start = Pose2D(0, 0, 0, 0)
    assert check_forward(start, Pose2D(20, 6, 0, 0))[0]
    assert not check_forward(start, Pose2D(20, 4, 0, 0))[0]      # not far enough
    assert not check_forward(start, Pose2D(25, 6, 0, 0))[0]      # too slow


def test_mean_yaw_rate_across_the_seam():
    # Turning counter-clockwise through +pi: 170 deg -> -170 deg is +20 deg, not -340.
    poses = [Pose2D(0, 0, 0, math.radians(170)), Pose2D(2, 0, 0, math.radians(-170))]
    assert mean_yaw_rate(poses) == pytest.approx(math.radians(10))


def test_check_turn_direction():
    ccw = [Pose2D(t, 0, 0, math.radians(5 * t)) for t in range(5)]
    assert check_turn(ccw, left_thrust=-200, right_thrust=200)[0]
    assert not check_turn(ccw, left_thrust=200, right_thrust=-200)[0]
    still = [Pose2D(t, 0, 0, 0.0) for t in range(5)]
    assert not check_turn(still, left_thrust=-200, right_thrust=200)[0]


def test_real_time_factor():
    assert real_time_factor(10, 20) == pytest.approx(0.5)
    assert check_real_time(0.6)[0]
    assert not check_real_time(0.4)[0]
    with pytest.raises(ValueError):
        real_time_factor(1, 0)
