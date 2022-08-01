#!/usr/bin/env python3
import unittest

from selfdrive.coachd.modules.tailgating_detection import (MINIMAL_VELOCITY,
                                                           THW_THRESHOLD,
                                                           TailgatingStatus,
                                                           is_tailgating)


class TestTailgatingDetection(unittest.TestCase):
  def setUp(self) -> None:
    self.TS = TailgatingStatus()

  def test_is_tailgating_velocity_higher_than_minimal(self) -> None:
    """"""
    velocity = MINIMAL_VELOCITY + 1
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertTrue(tailgating)

  def test_is_tailgating_velocity_equals_minimal(self) -> None:
    """"""
    velocity = MINIMAL_VELOCITY
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertTrue(tailgating)

  def test_not_tailgating_velocity_lower_than_minimal(self) -> None:
    """"""
    velocity = MINIMAL_VELOCITY - 1
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertFalse(tailgating)

  def test_not_tailgating_thw_equals_threshold(self) -> None:
    """"""
    thw = THW_THRESHOLD
    tailgating = is_tailgating(thw=thw, v_ego=10)
    self.assertFalse(tailgating)

  def test_is_tailgating_thw_lower_than_threshold(self) -> None:
    """"""
    thw = THW_THRESHOLD - 0.1
    tailgating = is_tailgating(thw=thw, v_ego=10)
    self.assertTrue(tailgating)


if __name__ == "__main__":
  unittest.main()
