import os
import can
import time

import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor


if __name__ == "__main__":
  core.CANHelper.init("can0")

  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
  # screw = CanScrewMotor(canBus, 0x145)
  joint1 = CanUJoint(can0, 0x141)
  # joint2 = CanUJoint(can0, 0x142)

  # Set the speeds for the motors
  joint1.speed_ctrl(2)
  # joint2.speed_ctrl(3)
  
  try:
    # Duration of motor spin in seconds
    time.sleep(3)
  except(KeyboardInterrupt) as e:
    print(e)
  
  # Set all the speeds to 0 and "stop" the motors
  # screw.speed_ctrl(0)
  joint1.speed_ctrl(0)
  # joint2.speed_ctrl(0)

  # screw.motor_stop()
  joint1.motor_stop()
  # joint2.motor_stop()

  print('Speed Test Done')

  core.CANHelper.cleanup("can0")