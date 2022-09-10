from cereal import log, messaging
from selfdrive.coachd.modules.base import CoachModule


THW_THRESHOLD = 1.  # in m, ego is tailgating when THW is below threshold
MINIMUM_VELOCITY = 5.  # in m/s, ego not tailgating when velocity below minimum

# all in s
TIME_TILL_LEVEL_1 = 5
TIME_TILL_LEVEL_2 = 10
TIME_TILL_LEVEL_3 = 20

# all in ns
LEVEL_1_THRESHOLD = int(TIME_TILL_LEVEL_1 * 1e+9)
LEVEL_2_THRESHOLD = int(TIME_TILL_LEVEL_2 * 1e+9)
LEVEL_3_THRESHOLD = int(TIME_TILL_LEVEL_3 * 1e+9)


def get_closest_lead(
    lead_one: log.RadarState.LeadData, lead_two: log.RadarState.LeadData
) -> log.RadarState.LeadData:
  # return nearest lead relative to ego
  return lead_one if lead_one.dRel <= lead_two.dRel else lead_two


def is_tailgating(thw: float, v_ego: float) -> bool:
  # ego is tailgating when thw of lead is between 0 and threshold,
  # and velocity of ego is greater than minimum
  return 0 < thw < THW_THRESHOLD and v_ego >= MINIMUM_VELOCITY


class TailgatingDetection(CoachModule):

  def __init__(self):
    self.measuring = False
    self.tailgating = False
    self.start_time = 0  # nanoseconds
    self.duration = 0  # nanoseconds

  @property
  def warning_level(self) -> int:
    if self.duration >= LEVEL_3_THRESHOLD:
      return 3
    if self.duration >= LEVEL_2_THRESHOLD:
      return 2
    if self.duration >= LEVEL_1_THRESHOLD:
      return 1
    return 0

  def update(
      self, sm: messaging.SubMaster) -> log.DrivingCoachState.TailgatingStatus:
    # if not sm.updated['radarState']:
    #   return self.create_tailgating_status()

    radar_state = sm['radarState']
    current_time = sm.logMonoTime['radarState']
    v_ego = sm['carState'].vEgo

    # get closest lead
    lead_one = radar_state.leadOne
    lead_two = radar_state.leadTwo
    closest_lead = get_closest_lead(lead_one, lead_two)

    # determine if ego is tailgating
    self.tailgating = is_tailgating(closest_lead.thw, v_ego)

    # start measurement if tailgating and not measuring yet
    if self.tailgating and not self.measuring:
      self.start_measurement(current_time)
    # stop measurement if not tailgating and still measuring
    elif not self.tailgating and self.measuring:
      self.stop_measurement()

    # calculate duration (0 when not measuring)
    self.duration = current_time - self.start_time if self.measuring else 0

    return self.create_tailgating_status()

  def create_tailgating_status(self) -> log.DrivingCoachState.TailgatingStatus:
    return {
      "active": True,
      "isTailgating": bool(self.tailgating),
      "duration": int(self.duration),
      "warningLevel": int(self.warning_level),
    }

  def start_measurement(self, mono_time: int) -> None:
    self.measuring = True
    self.start_time = mono_time

  def stop_measurement(self) -> None:
    self.measuring = False
    self.start_time = 0
