#!/usr/bin/env python3
from typing import Dict, Optional, Type, Union

from cereal import log, messaging
from selfdrive.coachd.modules.base import CoachModule
from selfdrive.coachd.modules.tailgating_detection import TailgatingStatus

# key must match the name of the field in DrivingCoachState
# module must be derived from base class CoachModule
COACH_MODULES = {
    # name of field: module
    "tailgatingStatus": TailgatingStatus,
}


class CoachD():
  def __init__(self, modules: Optional[Dict[str, Type[CoachModule]]] = None) -> None:
    # initialize modules
    if modules is None:
      modules = dict(COACH_MODULES)
    self.modules = {field: module() for field, module in modules.items()}
    # add field names to activated_fields
    self.activated_fields = [field for field in modules.keys()]
  
  def is_field_activated(self, field: str) -> bool:
    return field in self.activated_fields

  def update(self, sm: messaging.SubMaster) -> log.DrivingCoachState:
    dat = messaging.new_message('drivingCoachState')
    drivingCoachState = dat.drivingCoachState

    # *** validate services ***
    dat.valid = sm.all_checks(service_list=['carState', 'radarState'])

    # *** fill drivingCoachState fields ***
    for field, module in self.modules.items():
      setattr(drivingCoachState, field, module.update(sm))

    # *** publish drivingCoachState ***
    return dat


def coachd_thread(sm: Union[messaging.SubMaster, None] = None,
                  pm: Union[messaging.PubMaster, None] = None
                  ) -> None:

  # *** setup messaging ***
  if sm is None:
    sm = messaging.SubMaster(['carState', 'radarState'])
  if pm is None:
    pm = messaging.PubMaster(['drivingCoachState'])

  CD = CoachD()

  while True:
    sm.update()
    dat = CD.update(sm)
    pm.send('drivingCoachState', dat)


def main(sm: Union[messaging.SubMaster, None] = None,
         pm: Union[messaging.PubMaster, None] = None
         ) -> None:
  coachd_thread(sm, pm)


if __name__ == "__main__":
  main()
