#!/usr/bin/env python3
import unittest
from inspect import signature
from typing import Dict

from cereal import log, messaging
from selfdrive.coachd.coachd import COACH_MODULES, VALIDATED_SERVICES, CoachD
from selfdrive.coachd.modules.base import CoachModule


class CustomModule(CoachModule):

  def update(self, sm: messaging.SubMaster) -> Dict[str, int]:
    return {"warningLevel": 42}


class TestCoachD(unittest.TestCase):

  # capnp schema
  def test_DrivingCoachState_struct_defined(self):
    """Ensure DrivingCoachState struct is defined in capnp schema"""
    s = "DrivingCoachState"
    structs = [n.name for n in log.schema.get_proto().nestedNodes]
    self.assertTrue(s in structs, msg="%s struct not in schema" % (s))

  def test_drivingCoachState_defined(self):
    """Ensure drivingCoachState field is defined in capnp schema"""
    field = "drivingCoachState"
    messages = log.Event.schema.fieldnames
    self.assertTrue(field in messages, msg="%s not in Event schema" % (field))

  def test_default_modules_defined(self):
    """Ensure default modules are defined in capnp schema"""
    fieldnames = log.DrivingCoachState.schema.fieldnames
    for field in COACH_MODULES:
      fail_msg = "%s not in DrivingCoachState schema" % (field)
      self.assertTrue(field in fieldnames, msg=fail_msg)

  def test_default_modules_types_contain_active_field(self):
    """Ensure default modules structs contain a field named 'active' in capnp schema"""
    dcs_fields = log.DrivingCoachState.schema.fields
    for field in COACH_MODULES:
      module_schema = dcs_fields[field].schema
      name = module_schema.node.displayName
      fail_msg = "field 'active' not defined in %s schema" % (name)
      self.assertTrue("active" in module_schema.fieldnames, msg=fail_msg)

  def test_default_modules_types_active_field_is_bool(self):
    """Ensure default modules 'active' field is of type bool in capnp schema"""
    dcs_fields = log.DrivingCoachState.schema.fields
    for field in COACH_MODULES:
      module_schema = dcs_fields[field].schema
      name = module_schema.node.displayName
      d_type = module_schema.fields["active"].proto.to_dict()["slot"]["type"]
      fail_msg = "field 'active' not of type bool in %s schema" % (name)
      self.assertTrue("bool" in d_type, msg=fail_msg)

  # abstract base class
  def test_default_modules_derived_from_base(self):
    """"Verify default modules are derived from abstract base class"""
    for module in COACH_MODULES.values():
      fail_msg = "%s not derived from CoachModule" % (module.__name__)
      self.assertTrue(issubclass(module, CoachModule), msg=fail_msg)

  def test_default_modules_implement_update_method(self):
    """"Verify default modules implement update method"""
    for module in COACH_MODULES.values():
      fail_msg = "%s does not implement update method" % (module.__name__)
      self.assertTrue(callable(getattr(module, "update", None)), msg=fail_msg)

  def test_default_modules_update_method_takes_atleast_same_number_of_arguments_as_base(self):
    """Verify update methods takes at least same amount of arguments as base class"""
    CM_params = signature(CoachModule.update).parameters
    for module in COACH_MODULES.values():
      fail_msg = "update method of %s must have at least the same amount of arguments as CoachModule" % (module.__name__)
      module_params = signature(module.update).parameters
      self.assertEqual(len(CM_params), len(module_params), msg=fail_msg)

  # init
  def test_init_custom_module_added_to_modules(self):
    """Verify module passed in constructor is added to coachd modules"""
    CD = CoachD(modules={"custom_module": CustomModule})
    self.assertTrue("custom_module" in CD.modules,
                    msg="Module passed to init must be added to modules")

  def test_init_custom_module_is_sole_module_when_passed(self):
    """Verify module passed in constructor is sole module added"""
    CD = CoachD(modules={"custom_module": CustomModule})
    self.assertEqual(len(CD.modules), 1,
                     msg="custom_module should be the only added module")

  def test_init_default_modules_set_when_parameter_is_none(self):
    """Verify default modules are set when no argument given"""
    CD = CoachD()
    self.assertEqual(CD.modules.keys(), COACH_MODULES.keys(),
                     msg="modules attribute is not set with default modules (COACH_MODULES)")

  def test_init_custom_validation_service_added_to_list(self):
    """Verify service passed in constructor is added to validated services"""
    CD = CoachD(modules={}, validated_services=["custom_service"])
    self.assertTrue("custom_service" in CD.validated_services,
                    msg="Module passed to init must be added to validated services")

  def test_init_custom_validated_service_is_sole_service_when_passed(self):
    """Verify module passed in constructor is sole service added"""
    CD = CoachD(modules={}, validated_services=["custom_service"])
    self.assertEqual(len(CD.validated_services), 1,
                     msg="cusom_service should be the only added service")

  def test_init_default_validated_services_set_when_parameter_is_none(self):
    """Verify default validated services are set when no argument given"""
    CD = CoachD()
    self.assertEqual(CD.validated_services, VALIDATED_SERVICES,
                     msg="validated_services attribute is not set with default list (VALIDATED_SERVICES)")

  # active modules
  def test_module_is_active_when_passed_to_init(self):
    """"Verify module is active when passed to constructor"""
    CD = CoachD(modules={"custom_module": CustomModule})
    self.assertTrue(CD.is_module_active("custom_module"),
                    msg="Module passed to constructor must be active")

  def test_module_is_not_active_when_not_passed_to_init(self):
    """"Verify module is NOT active if NOT passed to constructor"""
    CD = CoachD(modules={})
    self.assertFalse(CD.is_module_active("custom_module"),
                     msg="module NOT passed in init must NOT be active")

  # update
  def test_update_returns_Event(self):
    """Verify returned object is of type Event"""
    sm = messaging.SubMaster([])
    CD = CoachD(modules={}, validated_services=[])
    dcs = CD.update(sm)
    dcs_type = dcs.schema.node.displayName
    event_type = log.Event.schema.node.displayName
    self.assertEqual(event_type, dcs_type,
                     msg="Returned object is of type %s" % (dcs_type))

  def test_update_returns_drivingCoachState_message(self):
    """Verify returned object contains a drivingCoachState message"""
    sm = messaging.SubMaster([])
    CD = CoachD(modules={}, validated_services=[])
    dcs = CD.update(sm)
    self.assertTrue("drivingCoachState" in dcs.to_dict(),
                     msg="Returned object does not contain drivingCoachState")

  def test_update_sets_field_with_value(self):
    """Verify update method sets the corresponding field with value"""
    sm = messaging.SubMaster([])
    field = "tailgatingStatus"
    CD = CoachD(modules={field: CustomModule}, validated_services=[])
    dcs = CD.update(sm)
    actual = dcs.drivingCoachState.tailgatingStatus.warningLevel
    expected = CustomModule().update(sm)['warningLevel']
    self.assertEqual(expected, actual,
                     msg="Failed to set '%s' field with value '%s'" % (field, expected))


if __name__ == "__main__":
  unittest.main()
