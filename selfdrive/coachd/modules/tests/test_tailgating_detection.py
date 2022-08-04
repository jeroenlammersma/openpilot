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

  # closest lead
  # TODO: add closest lead test(s)

  # is tailgating
  def test_is_tailgating_when_velocity_higher_than_minimum(self) -> None:
    """Verify is tailgating when velocity is higher than required minimum"""
    tailgating = is_tailgating(thw=0.5, v_ego=MINIMUM_VELOCITY + 1)
    self.assertTrue(
        tailgating, msg="Must be tailgating when v_ego higher than minumum")

  def test_is_tailgating_when_velocity_equals_minimum(self) -> None:
    """Verify is tailgating when velocity equals required minimum"""
    tailgating = is_tailgating(thw=0.5, v_ego=MINIMUM_VELOCITY)
    self.assertTrue(
        tailgating, msg="Must be tailgating when v_ego equals minumum")

  def test_not_tailgating_when_velocity_lower_than_minimum(self) -> None:
    """Verify not tailgating when velocity lower than required minimum"""
    tailgating = is_tailgating(thw=0.5, v_ego=MINIMUM_VELOCITY - 1)
    self.assertFalse(
        tailgating, msg="Must NOT be tailgating when v_ego lower than minimum")

  def test_not_tailgating_when_thw_equals_threshold(self) -> None:
    """Verify not tailgating when THW equals threshold"""
    tailgating = is_tailgating(thw=THW_THRESHOLD, v_ego=10)
    self.assertFalse(
        tailgating, msg="Must NOT be tailgating when thw equals threshold")

  def test_is_tailgating_when_thw_lower_than_threshold(self) -> None:
    """Verify is tailgating when THW is lower than threshold"""
    tailgating = is_tailgating(thw=THW_THRESHOLD - 0.1, v_ego=10)
    self.assertTrue(
        tailgating, msg="Must be tailgating when thw lower than threshold")

  # update
  # TODO: add update test(s)
  # TODO: def test_warning_level_is_zero_on_threshold_when_not_measuring(self) -> None:

  # start measurement
  def test_is_measuring_when_measurement_started(self) -> None:
    self.TS.start_measurement(0)
    self.assertTrue(self.TS.measuring,
                    msg="Must be measuring when measurement started")

  def test_start_time_set_to_mono_time_when_measurement_started(self) -> None:
    self.TS.start_measurement((mono_time := 42))
    self.assertEqual(mono_time, self.TS.start_time,
                     msg="start_time must be set to value of mono_time when measurement started")

  # stop measurement
  def test_not_measuring_when_measurement_stopped(self) -> None:
    self.TS.start_measurement(0)
    self.TS.stop_measurement()
    self.assertFalse(self.TS.measuring,
                     msg="Must NOT be measuring when measurement stopped")

  def test_start_time_reset_to_zero_when_measurement_stopped(self) -> None:
    self.TS.start_measurement(42)
    self.TS.stop_measurement()
    self.assertEqual(0, self.TS.start_time,
                     msg="start_time must be reset to zero when measurement stopped")

  # determine warning level
  def test_warning_level_is_zero_just_below_threshold(self) -> None:
    """Verify warning level is 0 just below level 1 threshold"""
    level = self.TS.determine_warning_level(LEVEL_1_THRESHOLD - 1)
    self.assertEqual(
        0, level, msg="Warning level must be 0, one nanosecond below level 1 threshold")

  def test_warning_level_is_one_on_threshold(self) -> None:
    """Verify warning level is 1 on level 1 threshold"""
    level = self.TS.determine_warning_level(LEVEL_1_THRESHOLD)
    self.assertEqual(
        1, level, msg="Warning level must be 1 on level 1 threshold")

  def test_warning_level_is_one_just_below_threshold(self) -> None:
    """Verify warning level is 1 just below level 2 threshold"""
    level = self.TS.determine_warning_level(LEVEL_2_THRESHOLD - 1)
    self.assertEqual(
        1, level, msg="Warning level must be 1, one nanosecond below level 2 threshold")

  def test_warning_level_is_two_on_threshold(self) -> None:
    """Verify warning level is 2 on level 2 threshold"""
    level = self.TS.determine_warning_level(LEVEL_2_THRESHOLD)
    self.assertEqual(
        2, level, msg="Warning level must be 2 on level 2 threshold")

  def test_warning_level_is_two_just_below_threshold(self) -> None:
    """Verify warning level is 2 just below level 3 threshold"""
    level = self.TS.determine_warning_level(LEVEL_3_THRESHOLD - 1)
    self.assertEqual(
        2, level, msg="Warning level must be 2, one nanosecond below level 3 threshold")

  def test_warning_level_is_three_on_threshold(self) -> None:
    """Verify warning level is 3 on level 3 threshold"""
    level = self.TS.determine_warning_level(LEVEL_3_THRESHOLD)
    self.assertEqual(
        3, level, msg="Warning level must be 3 on level 3 threshold")


if __name__ == "__main__":
  unittest.main()
