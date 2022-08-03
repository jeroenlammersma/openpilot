#!/usr/bin/env python3
import unittest

from cereal import log, messaging
from selfdrive.coachd.coachd import COACH_MODULES, CoachD
from selfdrive.coachd.modules.base import CoachModule


class TestCoachD(unittest.TestCase):

  def test_DrivingCoachState_struct_defined(self) -> None:
    """Ensure DrivingCoachState struct is defined in capnp schema"""
    s = "DrivingCoachState"
    structs = [n.name for n in log.schema.get_proto().nestedNodes]
    self.assertTrue(s in structs, msg="%s struct not in schema" % (s))

  def test_drivingCoachState_defined(self) -> None:
    """Ensure drivingCoachState field is defined in capnp schema"""
    field = "drivingCoachState"
    messages = log.Event.schema.fieldnames
    self.assertTrue(field in messages, msg="%s not in Event schema" % (field))

  def test_modules_defined(self) -> None:
    """Ensure COACH_MODULES are defined in capnp schema"""
    fieldnames = log.DrivingCoachState.schema.fieldnames

    for field in COACH_MODULES.keys():
      fail_msg = "%s not in DrivingCoachState schema" % (field)
      self.assertTrue(field in fieldnames, msg=fail_msg)

  def test_init_with_custom_module(self) -> None:
    """Verify module passed in constructor is added to coachd modules"""
    class CustomModule(CoachModule):
      def update(self, sm: messaging.SubMaster) -> None:
        return

    CD = CoachD(modules={"custom_module": CustomModule})
    self.assertTrue("custom_module" in CD.modules.keys(),
                    msg="Module passed to constructor not in modules")


if __name__ == "__main__":
  unittest.main()
