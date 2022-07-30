from cereal import log, messaging
from selfdrive.coachd.modules.base import CoachModule

THW_THRESHOLD = 1  # in m, ego is tailgating when THW is below threshold
MINIMAL_VELOCITY = 5  # in m/s, ego is not tailgating when velocity is below minimal

# all in s
TIME_TILL_LEVEL_1 = 5
TIME_TILL_LEVEL_2 = 10
TIME_TILL_LEVEL_3 = 20

# all in ns
LEVEL_1_THRESHOLD = TIME_TILL_LEVEL_1 * 1e+9
LEVEL_2_THRESHOLD = TIME_TILL_LEVEL_2 * 1e+9
LEVEL_3_THRESHOLD = TIME_TILL_LEVEL_3 * 1e+9


def get_closest_lead(lead_one: log.RadarState.LeadData,
                     lead_two: log.RadarState.LeadData
                     ) -> log.RadarState.LeadData:
  # return nearest lead relative to ego
  return lead_one if lead_one.dRel <= lead_two.dRel else lead_two


def is_tailgating(thw: float, v_ego: float) -> bool:
  # ego is tailgating when thw of lead is between 0 and threshold,
  # and velocity of ego is greater than minimum
  return thw != 0 and thw < THW_THRESHOLD and v_ego >= MINIMAL_VELOCITY


class TailgatingStatus(CoachModule):
  def __init__(self) -> None:
    self.start_time = 0
    self.v_ego = 0.

  def update(self, sm: messaging.SubMaster) -> log.DrivingCoachState.TailgatingStatus:
    radar_state = sm['radarState']
    if sm.updated['carState']:
      self.v_ego = sm['carState'].vEgo

    current_time = max(sm.logMonoTime.values())

    # get closest lead
    lead_one = radar_state.leadOne
    lead_two = radar_state.leadTwo
    closest_lead = get_closest_lead(lead_one, lead_two)

    # determine if ego is tailgating
    tailgating = is_tailgating(closest_lead.thw, self.v_ego)

    # if tailgating, start measurement if not already measuring
    if tailgating and not self.currently_measuring():
      self.start_measurement(current_time)
    # if not tailgating and currently measuring, stop measurement
    elif not tailgating and self.currently_measuring():
      self.stop_measurement()

    # determine warning level
    warning_level = self.determine_warning_level(current_time)

    # create TailgatingStatus
    return {
        "isTailgating": bool(tailgating),
        "startTime": int(self.start_time),
        "warningLevel": int(warning_level)
    }

  def currently_measuring(self) -> bool:
    return self.start_time > 0

  def start_measurement(self, mono_time: int) -> None:
    self.start_time = mono_time

  def stop_measurement(self) -> None:
    self.start_time = 0

  def determine_warning_level(self, mono_time: int) -> int:
    if not self.currently_measuring():  # level 0
      return 0

    ellapsed_time = mono_time - self.start_time
    if ellapsed_time >= LEVEL_3_THRESHOLD:
      return 3
    if ellapsed_time >= LEVEL_2_THRESHOLD:
      return 2
    if ellapsed_time >= LEVEL_1_THRESHOLD:
      return 1
    return 0
