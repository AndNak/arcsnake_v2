import os
import can
import numpy as np
import time

import core.CANHelper
from core.CanArduinoSensors import CanArduinoSensors

if __name__ == "__main__":
  core.CANHelper.init("can0")
  
  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
  deviceId = 0x01
  sensor = CanArduinoSensors(can0, deviceId)

  try:
  
    for _ in range(100):
        print(sensor.readHumidityAndTemperature())
        time.sleep(1)

  except (KeyboardInterrupt, ValueError) as e: # Kill with ctrl + c
    print(e)

  core.CANHelper.cleanup("can0")