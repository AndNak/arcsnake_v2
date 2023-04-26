from asyncore import loop
from audioop import mul
from cProfile import run
from doctest import run_docstring_examples
from os.path import dirname, realpath
from pdb import post_mortem
import sys
from unittest import mock

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


if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    gear_ratio = 11

    print("Trying to initialize motors")
    joint1 = CanMotor(can0, 1, gear_ratio)
    joint2 = CanMotor(can0, 4, gear_ratio)
    joint3 = CanMotor(can0, 3, gear_ratio)
    joint4 = CanMotor(can0, 6, gear_ratio)
    screw1 = CanMotor(can0, 0, 1)
    screw2 = CanMotor(can0, 2, 1)
    screw3 = CanMotor(can0, 5, 1)

    print('Motor initialization complete')
    
    input('Press Enter to read joint current pos')
    joint1_pos = joint1.read_multiturn_position()
    joint2_pos = joint2.read_multiturn_position()
    joint3_pos = joint3.read_multiturn_position()
    joint4_pos = joint4.read_multiturn_position()

    print('Joint 1 pos: ', joint1_pos)
    print('Joint 2 pos: ', joint2_pos)
    print('Joint 3 pos: ', joint3_pos)
    print('Joint 4 pos: ', joint4_pos)

    input('Press Enter to set joint current pos')
    joint1.pos_ctrl(joint1_pos) # set read pos
    joint2.pos_ctrl(joint2_pos) # set read pos
    joint3.pos_ctrl(joint3_pos) # set read pos
    joint4.pos_ctrl(joint4_pos) # set read pos

    input('Press Enter to spin screw motors')
    # Roll
    # screw1.speed_ctrl(10)
    # screw2.speed_ctrl(-10)
    # screw3.speed_ctrl(-10)

    # Torpedo
    factor = 8
    number_of_steps = 1000
    for i in range(number_of_steps):
        screw1.speed_ctrl((factor*5)*i/number_of_steps  + 2)
        screw1.clear_error_flag()
        screw2.speed_ctrl((factor*10)*i/number_of_steps + 2)
        screw2.clear_error_flag()
        screw3.speed_ctrl((factor*-5)*i/number_of_steps - 2)
        screw3.clear_error_flag()
        time.sleep(0.01)

    print(screw1.get_error_flag())
    print(screw2.get_error_flag())
    print(screw3.get_error_flag())

    input('Press Enter to stop motors')
    joint1.motor_off()
    joint2.motor_off()
    joint3.motor_off()
    joint4.motor_off()
    screw1.motor_off()
    screw2.motor_off()
    screw3.motor_off()

    print('Done')

    core.CANHelper.cleanup("can0")
