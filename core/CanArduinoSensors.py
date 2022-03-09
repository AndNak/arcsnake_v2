import os
import can
import math
from CanUtils import CanUtils
from timeout import timeout

class CanArduinoSensors(object):
  def __init__(self, bus, arduino_id):
    self.canBus = bus
    self.utils = CanUtils()
    self.id = arduino_id

  def send(self, data):
    msg = can.Message(arbitration_id=self.id, data=data, extended_id=False)
    self.canBus.send(msg)
    msg = self.canBus.recv()
    return msg

  @timeout(1)
  def readHumidityAndTemperature(self):
    # Uncomment to send a message 
    data = [0x12, 0x34, 0x56, 0x78, 0x90, 0xab, 0xcd, 0xef]

    msg = can.Message(arbitration_id=self.id, data=data, extended_id=False)
    self.canBus.send(msg)

    # Uncomment when the arduino is ready to send back!
    while True:
      try:
        msg = self.canBus.recv()
        if msg.arbitration_id == self.id:
          break
      except (KeyboardInterrupt, ValueError) as e:
        print(e)
        break

    return int(msg.data[-1]), int(msg.data[-2])