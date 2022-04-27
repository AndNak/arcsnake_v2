import can
import core.CANHelper
import time
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor

if __name__ == "__main__":
  core.CANHelper.init("can0") # Intiailize can0
  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan') # Create can bus object 

  testMotor = CanUJoint(can0, 0x141, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14) # Initialize motor with can bus object 

  message = [0xa2, 0x00, 0x00, 0x00, 0x00, 0x03, 0x4B, 0x52]
  testMotor.send(message)

  time.sleep(2)

  testMotor.motor_stop()

  print('Done')

  core.CANHelper.cleanup("can0")