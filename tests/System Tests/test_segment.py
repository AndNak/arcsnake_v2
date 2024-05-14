### Test script for validating single segment (screw motor + 2 joints)
from asyncore import loop
from audioop import mul
from cProfile import run
from doctest import run_docstring_examples
from os.path import dirname, realpath
from pdb import post_mortem
import sys
from unittest import mock
import csv

from more_itertools import sample
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
from core.CanMotor import CanMotor
from core.CanScrewMotor import CanScrewMotor
from core.timeout import TimeoutError
import math


if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    gear_ratio = 11

    folder = "tests/System Tests/PCBTesting"
    test_name = "4screws_2joints_test"

    print("Trying to initialize motors")
    screw1 = CanMotor(can0, 0, 1)
    joint1 = CanMotor(can0, 3, gear_ratio)
    joint2 = CanMotor(can0, 5, gear_ratio)
    print('Motor initialization complete')

    input('Press Enter to spin screw motor')
    command_speed = 10
    screw1.speed_ctrl(command_speed)

    input("Press Enter to spin joint motors.")
    for i in range(10000):
        # print(i)
        joint1.pos_ctrl(amp*math.pi*math.sin(2*math.pi*i/10000))
        joint2.pos_ctrl(amp*math.pi*math.cos(2*math.pi*i/10000))
    
        (joint_torque, joint_speed, joint_s_pos) = joint1.read_motor_status()
        joint_m_pos = joint1.read_multiturn_position()
        read_pos_joint.append(joint_m_pos)
        read_speeds_joint.append(joint_speed)
        read_torque_joint.append(joint_torque)

        time.sleep(0.001)


    input('Press Enter to stop motors')
    # joint1.motor_off()
    # joint2.motor_off()
    # # joint3.motor_off()
    # # joint4.motor_off()
    screw1.motor_off()
    # screw2.motor_off()
    # screw3.motor_off()
    # screw4.motor_off()
    # screw5.motor_off()

    print('Done')

    # plt.plot(motor_voltages)
    # plt.legend(["joint 3", "joint 5", "screw 9", "screw8", "screw6"]) #, "screw 3", "joint 1", "joint 2", "joint 3", "joint 4"])
    # plt.title(test_name)
    # plt.xlabel("time")
    # plt.ylabel("Motor Voltage")
    # plt.savefig(f"{folder}/{test_name}.png")
    # plt.show()

    core.CANHelper.cleanup("can0")

