import os
import can
import math
import time
import matplotlib.pyplot as plt
from datetime import datetime
from pyinstrument import Profiler

from CanJointMotor import CanJointMotor
from CanUJoint import CanUJoint
from CanScrewMotor import CanScrewMotor
from CanUtils import CanUtils

def init():
  os.system('sudo ifconfig can0 down')
  os.system('sudo ip link set can0 type can bitrate 1000000')
  os.system('sudo ifconfig can0 up')

def cleanup():
  os.system('sudo ifconfig can0 down')

def profile(screw):
  profiler = Profiler()
  profiler.start()

  for i in range(1000):
    screw.pos_ctrl(0x00, 0x41, 0x00, 0x00)
    screw.read_encoder()

  profiler.stop()
  print(profiler.output_text(unicode=True, color=True))

if __name__ == "__main__":
  init()
  
  canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
  # joint1 = CanJointMotor(canBus, 0x141)
  joint2 = CanUJoint(canBus, 0x145)
  # screw = CanScrewMotor(canBus, 0x145)
  utils = CanUtils()
  
  start = datetime.now()
  t = []

  # read_speeds_screw = []
  # set_speeds_screw = []
  # read_torques_screw = []

  read_speeds_joint = []
  set_speeds_joint = []
  read_torque_joint = []



  for i in range(1000):
    try:
      time_since_start = datetime.now() - start
      t.append(time_since_start.total_seconds())
      
      to_vel = 0

      set_speeds_joint.append(to_vel)
      joint2.pos_ctrl(to_vel)
      (joint2_torque, joint2_speed, _) = joint2.read_motor_status()
      (temp, voltage, err) = joint2.read_motor_err_and_voltage()
      print('temp', temp)
      print('voltage', voltage)
      print('err state', err)

      read_speeds_joint.append(joint2_speed)
      read_torque_joint.append(joint2_torque)


      loop_dur = datetime.now() - start - time_since_start
      # 10ms for each loop
      time.sleep(max(0, .1 - loop_dur.total_seconds()))
    except (KeyboardInterrupt, ValueError) as e:
      print(e)
      break

  screw.motor_stop()
  plt.plot(t,set_speeds_joint,'b-')
  plt.plot(t,set_speeds_joint,'r-')
  plt.plot(t,read_torque_joint,'g-')

  plt.xlabel('time (s)')
  plt.ylabel('speed (rad/s)')
  # plt.legend(["screw encoder speed", "screw set speed", "screw torque"])
  plt.show()

  cleanup()
