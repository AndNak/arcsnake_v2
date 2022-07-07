import os
import can
import math
from .CanUtils import CanUtils
from .timeout import timeout

class CanArduinoSensors(object):
  def __init__(self, bus, arduino_id):
    self.canBus = bus
    self.utils = CanUtils()
    self.id = arduino_id

  def send(self, data):
    msg = can.Message(arbitration_id=self.id, data=data, is_extended_id=False)
    self.canBus.send(msg)
    msg = self.canBus.recv()
    return msg

  @timeout(1)

  def readHumidityAndTemperature(self):
    data = [0, 0, 0, 0, 0, 0, 0, 0]

    msg = can.Message(arbitration_id=self.id, data=data, is_extended_id=False)
    self.canBus.send(msg)

    while True:
      try:
        msg = self.canBus.recv()
        if msg.arbitration_id == self.id:
          break
      except (KeyboardInterrupt, ValueError) as e:
        print(e)
        break

    return int(msg.data[-1]), int(msg.data[-2]), int(msg.data[-3]*100)