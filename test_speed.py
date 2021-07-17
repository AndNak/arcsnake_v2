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
  joint1 = CanJointMotor(canBus, 0x142)
  joint2 = CanJointMotor(canBus, 0x143)


  # Get position
  '''
  start = time.time()
  num_loops = 1000
  for i in range(num_loops):
    joint1.pos_ctrl(joint1.read_position)
    joint2.speed_ctrl(0.0)
    screw.speed_ctrl(0.0)

  print((time.time()-start)/num_loops/3)

  time.sleep(20)
'''

  # Set the speeds for the motors
  try:
    screw.speed_ctrl(5.0)
    joint1.speed_ctrl(2)
    joint2.speed_ctrl(1.0)

    # Duration of motor spin in seconds
    time.sleep(600)
  except(KeyboardInterrupt) as e:
    print(e)
  
  # Set all the speeds to 0 and "stop" the motors
  screw.speed_ctrl(0)
  joint1.speed_ctrl(0)
  joint2.speed_ctrl(0)

  screw.motor_stop()
  joint1.motor_stop()
  joint2.motor_stop()

  print('Speed Test Done')

  cleanup()