import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor

from os.path import dirname, realpath  
import sys
from core.CanMotor import CanMotor  
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  



if __name__ == "__main__":
  core.CANHelper.init("can0")
  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

  testMotor = CanUJoint(can0, 0x141, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
  
  print("Enter Desired Rotation(s)")
  
  try:
    while True: 
      val = float(input())
      testMotor.pos_ctrl(val * 2 * 3.14)
      print("moving to position")


  except(KeyboardInterrupt) as e:
    print(e)

  testMotor.motor_stop()

  print('Done')

  core.CANHelper.cleanup("can0")