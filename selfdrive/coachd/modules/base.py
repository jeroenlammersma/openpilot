from abc import ABC, abstractmethod

import capnp

from cereal import messaging


class CoachModule(ABC):

  @abstractmethod
  def update(
      self, sm: messaging.SubMaster) -> capnp.lib.capnp._DynamicStructBuilder:
    pass
