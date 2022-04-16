from os.path import dirname, realpath
import sys
arcsnake_v2_path = dirname(dirname(realpath(__file__)))
sys.path.append(arcsnake_v2_path)

import os
import can
import math as m
import numpy as np
import time
import matplotlib.pyplot as plt
from datetime import datetime
from pyinstrument import Profiler

import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanJointMotor import CanJointMotor
from core.CanScrewMotor import CanScrewMotor
import time

print("Starting")

if __name__ == "__main__":
  core.CANHelper.init("can0")

  can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
  joint1 = CanJointMotor(can0, 0x141)
  
  start = datetime.now()
  t = []

  read_pos_joint = []
  read_speeds_joint = []
  read_torque_joint = []
  loop_rate = []

  amplitude = 3*2*np.pi
  frequency = .05
  loop_rate = 0.01
  trajectory_time_length = 10 # in seconds

  num_time_steps = int(trajectory_time_length/loop_rate)
  for i in range(num_time_steps):
    strt_time = time.time()
    t = i*loop_rate
    pos = amplitude*frequency*np.cos(2*np.pi*frequency*t)
    joint1.speed_ctrl(pos)
    if time.time() - strt_time > loop_rate :
      print("Warning: time to execute loop is longer than loop_rate")
    time.sleep(loop_rate - (time.time() - strt_time))
  
    # time_since_start = datetime.now() - start
    # t.append(time_since_start.total_seconds())
    (joint1_torque, joint1_speed, joint1_pos) = joint1.read_motor_status()
    # (temp, voltage, err) = joint1.read_motor_err_and_voltage()
    # print('pos', joint1_pos)
    # print('speed', joint1_speed)
    # print('torque', joint1_torque)
    # print('temp', temp)
    # print('voltage', voltage)
    # print('err state', err)
    # print('___________')

    read_pos_joint.append(joint1_pos)
    read_speeds_joint.append(joint1_speed)
    read_torque_joint.append(joint1_torque)
    # loop_rate.append(time.time()-tic)

  try:
  	time.sleep(0)
  except(KeyboardInterrupt) as e:
    print(e)
  
  joint1.motor_stop()
  
  print('Loading plot')

  #plt.plot(t,np.reciprocal(loop_rate))

  plt.plot(read_pos_joint,'r-')
  plt.plot(read_speeds_joint,'b-')
  #plt.plot(t,read_torque_joint,'g-')
  # plt.xlabel('time (s)')
  # plt.ylabel('loop rate (hz)')
  # plt.legend(["screw encoder speed", "screw set speed", "screw torque"])
  plt.show()
  
  core.CANHelper.cleanup("can0")
 

print("Done")