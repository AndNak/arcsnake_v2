import os
import can
from CanJointMotor import CanJointMotor
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

  canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
  screw = CanScrewMotor(canBus, 0x141)
  screw.speed_ctrl(4.0)

  for _ in range(10000):
    try:
      print('screw',screw.read_torque())
    except(KeyboardInterrupt) as e:
      print(e)
      break

  screw.motor_stop()

  cleanup()