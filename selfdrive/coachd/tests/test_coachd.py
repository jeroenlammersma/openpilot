#!/usr/bin/env python3
import unittest
from typing import Dict

from cereal import messaging
from selfdrive.coachd.coachd import CoachD
from selfdrive.coachd.modules.base import CoachModule


class TestTailgatingDetection(unittest.TestCase):

  def test_init_with_custom_module(self) -> None:
    """"""
    
    class CustomModule(CoachModule):
      def update(self, sm: messaging.SubMaster) -> Dict[str, int]:
        return {"value": 42}

    module = CustomModule
    CD = CoachD(modules={"custom_module": module})
    self.assertTrue("custom_module" in CD.modules.keys())


if __name__ == "__main__":
  unittest.main()
