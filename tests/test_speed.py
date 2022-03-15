import os
import can
from CanUJoint import CanUJoint
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

  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
  # screw = CanScrewMotor(canBus, 0x145)
  joint1 = CanUJoint(can0, 0x143)
  joint2 = CanUJoint(can0, 0x142)

  # Set the speeds for the motors
  joint1.speed_ctrl(2)
  joint2.speed_ctrl(3)
  
  try:
    # Duration of motor spin in seconds
    time.sleep(7200)
  except(KeyboardInterrupt) as e:
    print(e)
  
  # Set all the speeds to 0 and "stop" the motors
  # screw.speed_ctrl(0)
  joint1.speed_ctrl(0)
  joint2.speed_ctrl(0)

  # screw.motor_stop()
  joint1.motor_stop()
  joint2.motor_stop()

  print('Speed Test Done')

  cleanup()