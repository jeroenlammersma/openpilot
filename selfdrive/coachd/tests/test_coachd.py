#!/usr/bin/env python3
import unittest
from inspect import signature

from cereal import log, messaging
from selfdrive.coachd.coachd import COACH_MODULES, CoachD
from selfdrive.coachd.modules.base import CoachModule


class TestCoachD(unittest.TestCase):

  # capnp schema
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

  def test_default_modules_defined(self) -> None:
    """Ensure default modules are defined in capnp schema"""
    fieldnames = log.DrivingCoachState.schema.fieldnames

    for field in COACH_MODULES.keys():
      fail_msg = "%s not in DrivingCoachState schema" % (field)
      self.assertTrue(field in fieldnames, msg=fail_msg)

  # abstract base class
  def test_default_modules_derived_from_base(self) -> None:
    """"Verify default modules are derived from abstract base class"""
    for module in COACH_MODULES.values():
      fail_msg = "%s not derived from CoachModule" % (module.__name__)
      self.assertTrue(issubclass(module, CoachModule), msg=fail_msg)

  def test_default_modules_implement_update_method(self) -> None:
    """"Verify default modules implement update method"""
    for module in COACH_MODULES.values():
      fail_msg = "%s does not implement update method" % (module.__name__)
      self.assertTrue(callable(getattr(module, "update", None)), msg=fail_msg)

  def test_default_modules_update_method_parameters_same_as_base(self) -> None:
    """Verify update method parameters of default modules are same as base"""
    sig = signature(CoachModule.update).parameters
    for module in COACH_MODULES.values():
      fail_msg = "%s signature differs from CoachModule" % (module.__name__)
      self.assertEqual(sig, signature(module.update).parameters, msg=fail_msg)

  # constructor
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
