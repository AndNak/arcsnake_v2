import os
import can
import numpy as np
import time

import core.CANHelper
from core.CanArduinoSensors import CanArduinoSensors

def printAllImuData(sensor):
  print("\n--------------------------------------\n")
  print("Calibration and Temp Data: ", sensor.readImuCalibrationAndTemp())
  print("Orientation Euler Angles: ", sensor.readImuOrientation())
  print("Orientation Quaternion: ", sensor.readImuQuaternion())
  print("Gyroscope: ", sensor.readImuGyroscope())
  print("Magnetometer: ", sensor.readImuMagnetometer())
  print("Accelerometer: ", sensor.readImuAccelerometer())
  print("Linear Acceleration: ", sensor.readImuLinearAccel())
  print("Gravity Vector: ", sensor.readImuGravity())
  print("\n--------------------------------------\n")
  

if __name__ == "__main__":
  core.CANHelper.init("can0")
  
  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
  deviceId = 0x01
  sensor = CanArduinoSensors(can0, deviceId)

  try:
  
    while True:
      # key = input("Press 'c' to read calibration and temp, or press 'o' to read orientation")
      # if key == 'c':
      #   print(sensor.readImuCalibrationAndTemp())
      # elif key == 'o':
      #   print(sensor.readImuOrientation())
      input("read")
      print("Humidity, Temp, and Pressure: ", sensor.readHumidityAndTemperature())
      printAllImuData(sensor)
      # time.sleep(1)

  except (KeyboardInterrupt, ValueError) as e: # Kill with ctrl + c
    print(e)

  core.CANHelper.cleanup("can0")