#!/usr/bin/env python3
import unittest

from selfdrive.coachd.modules.tailgating_detection import (LEVEL_1_THRESHOLD, LEVEL_2_THRESHOLD, LEVEL_3_THRESHOLD, MINIMUM_VELOCITY,
                                                           THW_THRESHOLD,
                                                           TailgatingStatus,
                                                           is_tailgating)


class TestTailgatingDetection(unittest.TestCase):
  def setUp(self) -> None:
    self.TS = TailgatingStatus()

  def test_is_tailgating_velocity_higher_than_minimum(self) -> None:
    """Verify is tailgating when velocity is higher than required minimum"""
    velocity = MINIMUM_VELOCITY + 1
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertTrue(tailgating)

  def test_is_tailgating_velocity_equals_minimum(self) -> None:
    """Verify is tailgating when velocity equals required minimum"""
    velocity = MINIMUM_VELOCITY
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertTrue(tailgating)

  def test_not_tailgating_velocity_lower_than_minimum(self) -> None:
    """Verify not tailgating when velocity lower than required minimum"""
    velocity = MINIMUM_VELOCITY - 1
    tailgating = is_tailgating(thw=0.5, v_ego=velocity)
    self.assertFalse(tailgating)

  def test_not_tailgating_thw_equals_threshold(self) -> None:
    """Verify not tailgating when THW equals threshold"""
    thw = THW_THRESHOLD
    tailgating = is_tailgating(thw=thw, v_ego=10)
    self.assertFalse(tailgating)

  def test_is_tailgating_thw_lower_than_threshold(self) -> None:
    """Verify is tailgating when THW is lower than threshold"""
    thw = THW_THRESHOLD - 0.1
    tailgating = is_tailgating(thw=thw, v_ego=10)
    self.assertTrue(tailgating)

  # TODO: simply tests below
  def test_warning_level_at_level_0_threshold_1_minus_1(self) -> None:
    """Verify warning level is 0 at level 1 threshold minus 1 nanosecond"""
    self.TS.start_time += 1 # needed so currently_measuring == True
    level = self.TS.determine_warning_level(LEVEL_1_THRESHOLD)
    self.assertEqual(0, level, msg="warning level must be 0 at level threshold 1 minus 1 ns")

  def test_warning_level_at_level_1_threshold(self) -> None:
    """Verify warning level is 1 at level 1 threshold"""
    self.TS.start_time += 1 # needed so currently_measuring == True
    level_1_threshold = LEVEL_1_THRESHOLD + 1 # need to adjust threshold
    level = self.TS.determine_warning_level(level_1_threshold)
    self.assertEqual(1, level, msg="warning level must be 1 at level threshold 1")

  def test_warning_level_at_level_1_threshold_2_minus_1(self) -> None:
    """Verify warning level is 1 at level 2 threshold minus 1 nanosecond"""
    self.TS.start_time += 1 # needed so currently_measuring == True
    level = self.TS.determine_warning_level(LEVEL_2_THRESHOLD)
    self.assertEqual(1, level, msg="warning level must be 1 at level threshold 2 minus 1 ns")

  def test_warning_level_at_level_2_threshold(self) -> None:
    """Verify warning level is 2 at level 2 threshold"""
    self.TS.start_time += 1 # needed so currently_measuring == True
    level_2_threshold = LEVEL_2_THRESHOLD + 1 # need to adjust threshold
    level = self.TS.determine_warning_level(level_2_threshold)
    self.assertEqual(2, level, msg="warning level must be 2 at level threshold 2")

  def test_warning_level_at_level_2_threshold_3_minus_1(self) -> None:
    """Verify warning level is 2 at level 3 threshold minus 1 nanosecond"""
    self.TS.start_time += 1 # needed so currently_measuring == True
    level = self.TS.determine_warning_level(LEVEL_3_THRESHOLD)
    self.assertEqual(2, level, msg="warning level must be 2 at level threshold 3 minus 1 ns")

  def test_warning_level_at_level_3_threshold(self) -> None:
    """Verify warning level is 3 at level 3 threshold"""
    self.TS.start_time += 1 # needed so currently_measuring == True
    level_3_threshold = LEVEL_3_THRESHOLD + 1 # need to adjust threshold
    level = self.TS.determine_warning_level(level_3_threshold)
    self.assertEqual(3, level, msg="warning level must be 3 at level threshold 3")

if __name__ == "__main__":
  unittest.main()
