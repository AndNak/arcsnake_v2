import os
import can
from CanUJoint import CanUJoint
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

  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
  joint1 = CanJointMotor(can0, 0x143)
  joint2 = CanJointMotor(can0, 0x142)

  # print('joint1 zero',joint1.zero_motor())
  # print('joint2 zero',joint2.zero_motor())

  # Read current position
  print('joint1',joint1.read_position())
  print('joint2',joint2.read_position())
  print('joint1 multiturn',joint1.read_multiturn_position())
  print('joint2 multiturn',joint2.read_multiturn_position())

  # Set all the speeds to 0 and "stop" the motors
  # screw.speed_ctrl(0)
  print("moving to zero position")
  joint1.pos_ctrl(20)
  joint2.pos_ctrl(20)
  
  try:
    time.sleep(1)
  except(KeyboardInterrupt) as e:
    print(e)

  # Read current position
  print('joint1',joint1.read_position())
  print('joint2',joint2.read_position())

  # screw.motor_stop()
  joint1.motor_stop()
  joint2.motor_stop()

  print('Joint Zeroing Test Done')

  cleanup()