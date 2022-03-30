import os
import can

from os.path import dirname, realpath  
import sys  
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  

import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanJointMotor import CanJointMotor
from core.CanScrewMotor import CanScrewMotor
import time

if __name__ == "__main__":
  core.CANHelper.init("can0")

  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
  joint1 = CanJointMotor(can0, 0x141)
  # joint2 = CanJointMotor(can0, 0x142)

  # print('joint1 zero',joint1.zero_motor())
  # print('joint2 zero',joint2.zero_motor())

  # Read current position
  print('joint1',joint1.read_position())
  #print('joint2',joint2.read_position())
  print('joint1 multiturn',joint1.read_multiturn_position())
  #print('joint2 multiturn',joint2.read_multiturn_position())

  # Set all the speeds to 0 and "stop" the motors
  # screw.speed_ctrl(0)
  print("moving to position")
  # joint1.pos_ctrl(20)
  joint1.pos_ctrl(1 * 2 * 3.1415)
  # joint2.pos_ctrl(20)
  
  try:
    time.sleep(1)
  except(KeyboardInterrupt) as e:
    print(e)

  # Read current position
  print('joint1',joint1.read_position())
  # print('joint2',joint2.read_position())

  # screw.motor_stop()
  joint1.motor_stop()
  # joint2.motor_stop()

  print('Done')

  core.CANHelper.cleanup("can0")