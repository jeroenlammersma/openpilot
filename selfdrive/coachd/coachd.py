#!/usr/bin/env python3
from typing import Dict, List, Optional, Type, Union

from cereal import log, messaging
from selfdrive.coachd.modules.base import CoachModule
from selfdrive.coachd.modules.tailgating_detection import TailgatingDetection

# key must match name of coresponding field in DrivingCoachState schema
COACH_MODULES: Dict[str, Type[CoachModule]] = {
    # fieldname: module
    "tailgatingStatus": TailgatingDetection,
}

# services that need to be validated to make a DrivingCoachState message valid
VALIDATED_SERVICES = ['carState', 'radarState']


class CoachD():
  def __init__(self,
               modules: Optional[Dict[str, Type[CoachModule]]] = None,
               validated_services: Optional[List[str]] = None
               ) -> None:

    # initialize modules
    if modules is None:
      modules = COACH_MODULES
    self.modules = {field: module() for field, module in modules.items()}

    # set services that need validation
    if validated_services is None:
      validated_services = VALIDATED_SERVICES
    self.validated_services = validated_services

  def is_field_active(self, field: str) -> bool:
    return field in self.modules.keys()

  def update(self, sm: messaging.SubMaster) -> log.DrivingCoachState:
    dat = messaging.new_message('drivingCoachState')
    drivingCoachState = dat.drivingCoachState

    # *** validate services ***
    dat.valid = sm.all_checks(service_list=self.validated_services)

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

    # do not publish new message if radarState not updated
    # (if check get's in your way, move this to TailgatingDetection.update(sm) method)
    if not sm.updated['radarState']:
      continue

    dat = CD.update(sm)
    pm.send('drivingCoachState', dat)


def main(sm: Union[messaging.SubMaster, None] = None,
         pm: Union[messaging.PubMaster, None] = None
         ) -> None:
  coachd_thread(sm, pm)


if __name__ == "__main__":
  main()
