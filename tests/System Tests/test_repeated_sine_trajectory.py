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

    folder = "tests/System Tests/JointRepeatabilityTests"
    test_name = "test1"

    print("Trying to initialize motors")
    # screw1 = CanMotor(can0, 0, 1)
    joint1 = CanMotor(can0, 8, gear_ratio)
    # joint2 = CanMotor(can0, 7, gear_ratio)
    print('Motor initialization complete')

    input("Press Enter to read zero position.")
    joint1_zero_pos = joint1.read_multiturn_position()

    amp = 0.1 * math.pi
    num_periods = 10
    t_period = 5 # s
    num_samples = 360 # per period
    
    log_data = [["time", "s_pos", "m_pos", "speed", "torque"]]
    input("Press Enter to start test.")
    print("Commanding to zero position...")
    joint1.pos_ctrl(joint1_zero_pos, 1)
    time.sleep(3)
    print("Starting Test.")
    t0 = time.time()
    for i in range(num_periods * num_samples + 1):

        joint1.pos_ctrl(amp*math.sin(2*math.pi*i/num_samples) + joint1_zero_pos)
        # joint2.pos_ctrl(amp*math.sin(2*math.pi*i/500 + math.pi/2) + joint2_zero_pos)
        cur_t = time.time() - t0
        (cur_torque, cur_speed, cur_s_pos) = joint1.read_motor_status()
        cur_m_pos = joint1.read_multiturn_position()
        log_data.append([cur_t, cur_s_pos, cur_m_pos, cur_speed, cur_torque])
        print(f"Iteration {i}\n-------------\n")
        print(f"Time = {cur_t}, {joint1.read_motor_status()}")
        time.sleep(t_period / num_samples)

    joint1.motor_stop()    
    # joint2.motor_stop()    

    print('Test Done')

    # Save data to csv
    with open(os.path.join(folder, f"{test_name}.csv"), 'w') as f:
        writer = csv.writer(f)
        writer.writerows(log_data)

    # Plot sine waves on top of eachother
    log_data = np.array(log_data[1:])
    t = log_data[:,0]
    s_pos = log_data[:,1]
    m_pos = log_data[:,2]
    speed = log_data[:,3]
    torque = log_data[:,4]
    fig, axs = plt.subplots(4, 1)
    # fig.suptitle("Position")
    for i in range(num_periods):
        start_idx = i*num_samples
        end_idx = (i+1)*num_samples + 1

        axs[0].set_title("Singlturn Position")
        axs[0].plot(t[start_idx:end_idx], s_pos[start_idx:end_idx], label=f"Period {i+1}")

        axs[1].set_title("Mutliturn Position")
        axs[1].plot(t[start_idx:end_idx], m_pos[start_idx:end_idx])

        axs[2].set_title("Speed")
        axs[2].plot(t[start_idx:end_idx], speed[start_idx:end_idx])

        axs[3].set_title("Torque")
        axs[3].plot(t[start_idx:end_idx], torque[start_idx:end_idx])

        axs[0].legend()

    plt.show()

    joint1.motor_off()
    core.CANHelper.cleanup("can0")

