import os
import can
from CanScrewMotor import CanScrewMotor
import time

def init():
  os.system('sudo ifconfig can0 down')
  os.system('sudo ip link set can0 type can bitrate 1000000')
  os.system('sudo ifconfig can0 up')

def cleanup():
  os.system('sudo ifconfig can0 down')

if __name__ == "__main__":
  init()

  canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan')

  screw = CanScrewMotor(canBus, 0x141)

  # Set the speeds for the motors
  try:
    screw.speed_ctrl(1)
    
    # Duration of motor spin in seconds
    time.sleep(60)
  except(KeyboardInterrupt) as e:
    print(e)
  
  # Set all the speeds to 0 and "stop" the motors
  screw.speed_ctrl(0)
  screw.motor_stop()

  print('Experiment Testing Done!')

  cleanup()