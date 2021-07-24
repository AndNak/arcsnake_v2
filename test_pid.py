import os
import can
import math
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
  pos = screw.read_position()
  screw.pos_pid_ctrl(100, 100)
  screw.speed_pid_ctrl(40, 30)
  screw.torque_pid_ctrl(50, 50)
  screw.pos_ctrl(pos) # this doesn't work, see position control command 4 on the datasheet
  # set direction in the U-joint using spin direction relative to current position
  
  try:
    print('screw read position', pos)
    
    (pos_p, pos_i, speed_p, speed_i, torque_p, torque_i) = screw.read_motor_pid()
    print('pos_p',pos_p)
    print('pos_i',pos_i)
    print('speed_p',speed_p)
    print('speed_i',speed_i)
    print('torque_p',torque_p)
    print('torque_i',torque_i)
    time.sleep(10)
    
  except (KeyboardInterrupt, ValueError) as e:
    print(e)

  screw.motor_stop()
  cleanup()