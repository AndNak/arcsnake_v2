import os
import can
from CanJointMotor import CanJointMotor
from CanScrewMotor import CanScrewMotor
from CanUJoint import CanUJoint
import time
from CanArduinoSensors import CanArduinoSensors
import numpy as np

def init():
  os.system('sudo ifconfig can0 down')
  os.system('sudo ip link set can0 type can bitrate 1000000')
  os.system('sudo ifconfig can0 up')

def cleanup():
  os.system('sudo ifconfig can0 down')


if __name__ == "__main__":
  init()
  
  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
  deviceId = 0x01
  sensor = CanArduinoSensors(can0, deviceId)

  # screw1 = CanScrewMotor(can0, 0x141)
  joint1 = CanUJoint(can0, 0x142)
  joint2 = CanUJoint(can0, 0x143)

  try:
  
    for _ in range(1000):
        # print('screw1',screw1.read_position())
        print('joint1',joint1.read_position())
        print('joint2',joint2.read_position())
        # print(sensor.readHumidityAndTemperature())
        time.sleep(0.1)

  except (KeyboardInterrupt, ValueError) as e:
    print(e)

  # screw1.motor_stop()
  joint1.motor_stop()
  joint2.motor_stop()

  cleanup()