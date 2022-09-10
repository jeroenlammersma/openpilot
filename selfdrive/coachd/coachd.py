#!/usr/bin/env python3
from typing import Dict, List, Optional, Type

from cereal import log, messaging
from selfdrive.coachd.modules.base import CoachModule
from selfdrive.coachd.modules.tailgating_detection import TailgatingDetection


# key must match name of corresponding field in DrivingCoachState schema
COACH_MODULES: Dict[str, Type[CoachModule]] = {
  # fieldname: module
  "tailgatingStatus": TailgatingDetection,
}

# services that need to be validated to make a DrivingCoachState message valid
VALIDATED_SERVICES = ['carState', 'radarState']


class CoachD(object):

  def __init__(
      self,
      modules: Optional[Dict[str, Type[CoachModule]]] = None,
      validated_services: Optional[List[str]] = None
  ):
    # initialize modules
    if modules is None:
      modules = COACH_MODULES
    self.modules = {field: module() for field, module in modules.items()}

    # set services that need validation
    if validated_services is None:
      validated_services = VALIDATED_SERVICES
    self.validated_services = validated_services

  def is_module_active(self, module: str) -> bool:
    return module in self.modules

  def update(self, sm: messaging.SubMaster) -> log.Event:
    dat = messaging.new_message('drivingCoachState')

    # validate services
    dat.valid = sm.all_checks(service_list=self.validated_services)

    # fill drivingCoachState fields
    drivingCoachState = dat.drivingCoachState
    for field, module in self.modules.items():
      setattr(drivingCoachState, field, module.update(sm))

    return dat


def coachd_thread(
    sm: Optional[messaging.SubMaster] = None,
    pm: Optional[messaging.PubMaster] = None
):
  # *** setup messaging ***
  if sm is None:
    sm = messaging.SubMaster(['carState', 'radarState'])
  if pm is None:
    pm = messaging.PubMaster(['drivingCoachState'])

  CD = CoachD()

  while True:
    sm.update()

    # not necessary to publish new message if radarState not updated
    # (if this check needs to be renoved, move it to 'update' method of TailgatingDetection)
    if not sm.updated['radarState']:
      continue

    # *** publish drivingCoachState ***
    dat = CD.update(sm)
    pm.send('drivingCoachState', dat)


def main(
    sm: Optional[messaging.SubMaster] = None,
    pm: Optional[messaging.PubMaster] = None
):
  coachd_thread(sm, pm)


if __name__ == "__main__":
  main()
