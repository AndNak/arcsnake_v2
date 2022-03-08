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

  canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
  deviceId = 0x01
  sensor = CanArduinoSensors(canBus, deviceId)

  screw = CanScrewMotor(canBus, 0x141)
  joint1 = CanJointMotor(canBus, 0x143)
  joint2 = CanJointMotor(canBus, 0x145)

  # Set the speeds for the motors
  try:
    screw.speed_ctrl(10)
    joint1.speed_ctrl(0)
    joint2.speed_ctrl(0)

    # Read humidity sensor and set time
    start_time = time.time()
    print(start_time)
    while time.time() - start_time < 60*10:
      print(sensor.readHumidityAndTemperature())
      time.sleep(1)
  except(KeyboardInterrupt) as e:
    print(e)
  
  # Set all the speeds to 0 and "stop" the motors
  screw.speed_ctrl(0)
  joint1.speed_ctrl(0)
  joint2.speed_ctrl(0)

  screw.motor_stop()
  joint1.motor_stop()
  joint2.motor_stop()

  print('Experiment Testing Done!')

  cleanup()