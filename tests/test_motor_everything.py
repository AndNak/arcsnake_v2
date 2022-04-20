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
  core.CANHelper.init("can0") # Intiailize can0
  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan') # Create can bus object 

  testMotor = CanUJoint(can0, 0x141, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14) # Initialize motor with can bus object 

  print("Enter Desired Control method")
  print("1 = Position Control (Rotations)")
  print("2 = Velocity Control (Rotations Per Second)")
  print("3 = Torque Control (Amps)")

  controlMethod = 0

  controlMethod = int(input())
   
  try:
    while True: 
      val = float(input())
      if controlMethod == 1:
        testMotor.pos_ctrl(val * 2 * 3.14) 
      elif controlMethod == 2:
        testMotor.speed_ctrl(val * 2 * 3.14)
      elif controlMethod == 3:
        testMotor.torque_ctrl(val)
      else:
        raise KeyboardInterrupt

  except(KeyboardInterrupt) as e:
    print(e)

  testMotor.motor_stop()

  print('Done')

  core.CANHelper.cleanup("can0")