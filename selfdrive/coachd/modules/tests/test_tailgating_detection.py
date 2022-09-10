#!/usr/bin/env python3
import unittest
from typing import Optional

from cereal import car, log, messaging
from selfdrive.coachd.modules.tailgating_detection import (LEVEL_1_THRESHOLD,
                                                           LEVEL_2_THRESHOLD,
                                                           LEVEL_3_THRESHOLD,
                                                           MINIMUM_VELOCITY,
                                                           THW_THRESHOLD,
                                                           TailgatingDetection,
                                                           get_closest_lead,
                                                           is_tailgating)


def mock_tailgating_scenario(
    sm: messaging.SubMaster,
    td: TailgatingDetection,
    v_ego: float,
    thw: float,
    duration: int
) -> log.DrivingCoachState.TailgatingStatus:
  sm = messaging.SubMaster(['carState', 'radarState'])
  mock_send_car_state(sm, v_ego)
  mock_send_radar_state(sm, lead_one_thw=thw)
  td.update(sm)
  mock_send_radar_state(sm, lead_one_thw=thw, log_mono_time=duration)
  ts = td.update(sm)
  return ts


def mock_send_car_state(sm: messaging.SubMaster, v_ego: float = .0) -> None:
  cs = car.CarState.new_message(vEgo=v_ego)
  sm.updated['carState'] = True
  sm.data['carState'] = cs


def mock_send_radar_state(
    sm: messaging.SubMaster,
    lead_one_d_rel: float = .0,
    lead_one_thw: float = .0,
    lead_two_d_rel: Optional[float] = None,
    lead_two_thw: Optional[float] = None,
    log_mono_time: int = 0
) -> None:
  rs = get_mock_radar_state(lead_one_d_rel, lead_one_thw,
                            lead_two_d_rel, lead_two_thw)
  sm.updated['radarState'] = True
  sm.data['radarState'] = rs
  sm.logMonoTime['radarState'] = log_mono_time


def get_mock_radar_state(
    lead_one_d_rel: float = .0,
    lead_one_thw: float = .0,
    lead_two_d_rel: Optional[float] = None,
    lead_two_thw: Optional[float] = None
) -> log.RadarState:
  # set lead two drel same as lead one if None
  if not lead_two_d_rel:
    lead_two_d_rel = lead_one_d_rel
  # set lead two thw same as lead one if None
  if not lead_two_thw:
    lead_two_thw = lead_one_thw

  return log.RadarState.new_message(
    leadOne=get_mock_lead_data(lead_one_d_rel, lead_one_thw),
    leadTwo=get_mock_lead_data(lead_two_d_rel, lead_two_thw)
  )


def get_mock_lead_data(d_rel: float, thw: float) -> log.RadarState.LeadData:
  return log.RadarState.LeadData.new_message(dRel=d_rel, thw=thw)


class TestTailgatingDetection(unittest.TestCase):

  def setUp(self):
    self.TD = TailgatingDetection()
    self.SM = messaging.SubMaster(['carState', 'radarState'])

  # capnp schema
  def test_TailgatingStatus_struct_defined(self):
    """Ensure TailgatingStatus struct is defined in capnp schema"""
    struct = "TailgatingStatus"
    dcs_schema = log.DrivingCoachState.schema
    structs = [n.name for n in dcs_schema.get_proto().nestedNodes]
    self.assertTrue(struct in structs, msg="%s struct not in schema" % (struct))

  # closest lead
  def test_lead_one_is_closest(self):
    """Verify lead one is closest when distance is lower than lead two"""
    rs = get_mock_radar_state(lead_one_d_rel=4.2, lead_two_d_rel=4.201)
    l1 = rs.leadOne
    l2 = rs.leadTwo
    self.assertEqual(l1, get_closest_lead(l1, l2),
                     msg="\nLead one must be closest (leadOne.dRel=%.3f, leadTwo.dRel=%.3f)" % (l1.dRel, l2.dRel))

  def test_lead_two_is_closest(self):
    """Verify lead two is closest when distance is lower than lead one"""
    dat = get_mock_radar_state(lead_one_d_rel=4.201, lead_two_d_rel=4.2)
    l1 = dat.leadOne
    l2 = dat.leadTwo
    self.assertEqual(l2, get_closest_lead(l1, l2),
                     msg="\nLead two must be closest (leadOne.dRel=%.3f, leadTwo.dRel=%.3f)" % (l1.dRel, l2.dRel))

  # is tailgating
  def test_is_tailgating_when_velocity_higher_than_minimum(self):
    """Verify is tailgating when velocity is higher than required minimum"""
    tailgating = is_tailgating(thw=0.5, v_ego=MINIMUM_VELOCITY + 1)
    self.assertTrue(
      tailgating, msg="Must be tailgating when v_ego higher than minimum")

  def test_is_tailgating_when_velocity_equals_minimum(self):
    """Verify is tailgating when velocity equals required minimum"""
    tailgating = is_tailgating(thw=0.5, v_ego=MINIMUM_VELOCITY)
    self.assertTrue(
      tailgating, msg="Must be tailgating when v_ego equals minimum")

  def test_not_tailgating_when_velocity_lower_than_minimum(self):
    """Verify not tailgating when velocity lower than required minimum"""
    tailgating = is_tailgating(thw=0.5, v_ego=MINIMUM_VELOCITY - 1)
    self.assertFalse(
      tailgating, msg="Must NOT be tailgating when v_ego lower than minimum")

  def test_not_tailgating_when_thw_equals_threshold(self):
    """Verify not tailgating when THW equals threshold"""
    tailgating = is_tailgating(thw=THW_THRESHOLD, v_ego=10)
    self.assertFalse(
      tailgating, msg="Must NOT be tailgating when thw equals threshold")

  def test_is_tailgating_when_thw_lower_than_threshold(self):
    """Verify is tailgating when THW is lower than threshold"""
    tailgating = is_tailgating(thw=THW_THRESHOLD - 0.1, v_ego=10)
    self.assertTrue(
      tailgating, msg="Must be tailgating when thw lower than threshold")

  # update
  def test_update_returns_TailgatingStatus(self):
    """Verify update method returns a TailgatingStatus object"""
    ts = log.DrivingCoachState.TailgatingStatus.new_message()
    ts_keys = ts.to_dict(verbose=True).keys()
    returned_keys = self.TD.update(self.SM).keys()
    self.assertEqual(ts_keys, returned_keys,
                     msg="Return object differs from TailgatingStatus")

  def test_active_is_true_when_updating(self):
    """Verify active is set to True when new tailgating status is requested"""
    tailgating_status = self.TD.update(self.SM)
    self.assertTrue(tailgating_status['active'],
                    msg="active must be set to true when updating")

  def test_update_returns_correct_values_when_not_tailgating_thw(self):
    """Verify update method returns expected tailgatingStatus when NOT tailgating due to thw being too high"""
    expected_status = {'active': True, 'isTailgating': False,
                       'duration': 0, 'warningLevel': 0}
    actual_status = mock_tailgating_scenario(
      self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD,
      duration=LEVEL_3_THRESHOLD)
    self.assertEqual(expected_status, actual_status,
                     msg="Update return differs from expected tailgatingStatus")

  def test_update_returns_correct_values_when_not_tailgating_velocity(self):
    """Verify update method returns expected tailgatingStatus when NOT tailgating due to velocity being too low"""
    expected_status = {'active': True, 'isTailgating': False,
                       'duration': 0, 'warningLevel': 0}
    actual_status = mock_tailgating_scenario(
      self.SM, self.TD, v_ego=MINIMUM_VELOCITY - 0.1, thw=THW_THRESHOLD - 0.5,
      duration=LEVEL_3_THRESHOLD)
    self.assertEqual(expected_status, actual_status,
                     msg="Update return differs from expected tailgatingStatus")

  def test_warning_level_is_zero_just_below_threshold(self):
    """Verify warning level is 0 just below level 1 threshold"""
    expected_status = {'active': True, 'isTailgating': True,
                       'duration': LEVEL_1_THRESHOLD - 1, 'warningLevel': 0}
    actual_status = mock_tailgating_scenario(
      self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD - 0.5,
      duration=LEVEL_1_THRESHOLD - 1)
    self.assertEqual(expected_status, actual_status,
                     msg="Warning level must be 0, one nanosecond below level 1 threshold")

  def test_warning_level_is_one_on_threshold(self):
    """Verify warning level is 1 on level 1 threshold"""
    expected_status = {'active': True, 'isTailgating': True,
                       'duration': LEVEL_1_THRESHOLD, 'warningLevel': 1}
    actual_status = mock_tailgating_scenario(
      self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD - 0.5,
      duration=LEVEL_1_THRESHOLD)
    self.assertEqual(expected_status, actual_status,
                     msg="Warning level must be 1 on level 1 threshold")

  def test_warning_level_is_one_just_below_threshold(self):
    """Verify warning level is 1 just below level 2 threshold"""
    expected_status = {'active': True, 'isTailgating': True,
                       'duration': LEVEL_2_THRESHOLD - 1, 'warningLevel': 1}
    actual_status = mock_tailgating_scenario(
      self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD - 0.5,
      duration=LEVEL_2_THRESHOLD - 1)
    self.assertEqual(expected_status, actual_status,
                     msg="Warning level must be 1, one nanosecond below level 2 threshold")

  def test_warning_level_is_two_on_threshold(self):
    """Verify warning level is 2 on level 2 threshold"""
    expected_status = {'active': True, 'isTailgating': True,
                       'duration': LEVEL_2_THRESHOLD, 'warningLevel': 2}
    actual_status = mock_tailgating_scenario(
      self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD - 0.5,
      duration=LEVEL_2_THRESHOLD)
    self.assertEqual(expected_status, actual_status,
                     msg="Warning level must be 2 on level 2 threshold")

  def test_warning_level_is_two_just_below_threshold(self):
    """Verify warning level is 2 just below level 3 threshold"""
    expected_status = {'active': True, 'isTailgating': True,
                       'duration': LEVEL_3_THRESHOLD - 1, 'warningLevel': 2}
    actual_status = mock_tailgating_scenario(
        self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD - 0.5,
        duration=LEVEL_3_THRESHOLD - 1)
    self.assertEqual(expected_status, actual_status,
                     msg="Warning level must be 2, one nanosecond below level 3 threshold")

  def test_warning_level_is_three_on_threshold(self):
    """Verify warning level is 3 on level 3 threshold"""
    expected_status = {'active': True, 'isTailgating': True,
                       'duration': LEVEL_3_THRESHOLD, 'warningLevel': 3}
    actual_status = mock_tailgating_scenario(
        self.SM, self.TD, v_ego=MINIMUM_VELOCITY, thw=THW_THRESHOLD - 0.5,
        duration=LEVEL_3_THRESHOLD)
    self.assertEqual(expected_status, actual_status,
                     msg="Warning level must be 3 on level 3 threshold")

  # start measurement
  def test_is_measuring_when_measurement_started(self):
    """"Verify tailgating is being measured when measurement started"""
    self.TD.start_measurement(0)
    self.assertTrue(self.TD.measuring,
                    msg="Must be measuring when measurement started")

  def test_start_time_set_to_mono_time_when_measurement_started(self):
    """Verify start time is set to given mono time when measurement started"""
    self.TD.start_measurement((mono_time := 42))
    self.assertEqual(mono_time, self.TD.start_time,
                     msg=("start time must be set to value of mono time when measurement started"))

  # stop measurement
  def test_not_measuring_when_measurement_stopped(self):
    """"Verify tailgating is stopped being measured when measurement stopped"""
    self.TD.start_measurement(0)
    self.TD.stop_measurement()
    self.assertFalse(self.TD.measuring,
                     msg="Must NOT be measuring when measurement stopped")

  def test_start_time_reset_to_zero_when_measurement_stopped(self):
    """Verify start time is reset to zero when measurement stopped"""
    self.TD.start_measurement(42)
    self.TD.stop_measurement()
    self.assertEqual(0, self.TD.start_time,
                     msg="start time must be reset when measurement stopped")


if __name__ == "__main__":
  unittest.main()
