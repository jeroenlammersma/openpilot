#!/usr/bin/env python3
import unittest

from selfdrive.coachd.modules.tailgating_detection import (LEVEL_1_THRESHOLD,
                                                           LEVEL_2_THRESHOLD,
                                                           LEVEL_3_THRESHOLD,
                                                           MINIMUM_VELOCITY,
                                                           THW_THRESHOLD,
                                                           TailgatingStatus,
                                                           is_tailgating)


class TestTailgatingDetection(unittest.TestCase):
  def setUp(self) -> None:
    self.TS = TailgatingStatus()

  # is_tailgating
  def test_is_tailgating_when_velocity_higher_than_minimum(self) -> None:
    """Verify is tailgating when velocity is higher than required minimum"""
    velocity = MINIMUM_VELOCITY + 1
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertTrue(tailgating)

  def test_is_tailgating_when_velocity_equals_minimum(self) -> None:
    """Verify is tailgating when velocity equals required minimum"""
    velocity = MINIMUM_VELOCITY
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertTrue(tailgating)

  def test_not_tailgating_when_velocity_lower_than_minimum(self) -> None:
    """Verify not tailgating when velocity lower than required minimum"""
    velocity = MINIMUM_VELOCITY - 1
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertFalse(tailgating)

  def test_not_tailgating_when_thw_equals_threshold(self) -> None:
    """Verify not tailgating when THW equals threshold"""
    thw = THW_THRESHOLD
    tailgating = is_tailgating(thw=thw, v_ego=10)
    self.assertFalse(tailgating)

  def test_is_tailgating_when_thw_lower_than_threshold(self) -> None:
    """Verify is tailgating when THW is lower than threshold"""
    thw = THW_THRESHOLD - 0.1
    tailgating = is_tailgating(thw=thw, v_ego=10)
    self.assertTrue(tailgating)

  # warning level
  def test_warning_level_is_zero_just_below_threshold(self) -> None:
    """Verify warning level is 0 just below level 1 threshold"""
    self.TS.measuring = True
    level = self.TS.determine_warning_level(LEVEL_1_THRESHOLD - 1)
    self.assertEqual(
        0, level, msg="Warning level must be 0, one nanosecond below level 1 threshold")

  def test_warning_level_is_one_on_threshold(self) -> None:
    """Verify warning level is 1 on level 1 threshold"""
    self.TS.measuring = True
    level = self.TS.determine_warning_level(LEVEL_1_THRESHOLD)
    self.assertEqual(
        1, level, msg="Warning level must be 1 on level 1 threshold")

  def test_warning_level_is_one_just_below_threshold(self) -> None:
    """Verify warning level is 1 just below level 2 threshold"""
    self.TS.measuring = True
    level = self.TS.determine_warning_level(LEVEL_2_THRESHOLD - 1)
    self.assertEqual(
        1, level, msg="Warning level must be 1, one nanosecond below level 2 threshold")

  def test_warning_level_is_two_on_threshold(self) -> None:
    """Verify warning level is 2 on level 2 threshold"""
    self.TS.measuring = True
    level = self.TS.determine_warning_level(LEVEL_2_THRESHOLD)
    self.assertEqual(
        2, level, msg="Warning level must be 2 on level 2 threshold")

  def test_warning_level_is_two_just_below_threshold(self) -> None:
    """Verify warning level is 2 just below level 3 threshold"""
    self.TS.measuring = True
    level = self.TS.determine_warning_level(LEVEL_3_THRESHOLD - 1)
    self.assertEqual(
        2, level, msg="Warning level must be 2, one nanosecond below level 3 threshold")

  def test_warning_level_is_three_on_threshold(self) -> None:
    """Verify warning level is 3 on level 3 threshold"""
    # self.TS.measuring = True
    level = self.TS.determine_warning_level(LEVEL_3_THRESHOLD)
    self.assertEqual(
        3, level, msg="Warning level must be 3 on level 3 threshold")


if __name__ == "__main__":
  unittest.main()
