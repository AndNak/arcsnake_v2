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

import matplotlib.pyplot as plt
import numpy as np

if __name__ == "__main__":
    # Initilize Can Bus
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    # Initialize Motor
    print("Trying to initialize motors")
    screw1 = CanMotor(can0, 0, 1)
    try:
        # original torque PI values: (50, 50)
        screw1.set_PI_values(None, None, None, None, 10, 250)
    except:
        print("Error setting PI values")
    print('Motor initialization complete')
    
    # Move Motor
    input('Press Enter to spin screw motors')
    torque_input = 0.4
    screw1.torque_ctrl(torque_input)

    # Read Torque
    torque_list = []
    while input("press 0 to stop motors") != "0":
        torque_sum = 0
        for i in range(0,100):
            torque = screw1.read_torque()
            torque_sum += torque
        torque_list.append(torque_sum/100)

    # Stop Motor
    screw1.motor_off()
    print('Done')

    # Can Bus Cleanup
    core.CANHelper.cleanup("can0")

    # Plot Torque vs. Instances
    torque_array = np.array(torque_list)
    element = np.arange(0, len(torque_array), 1)
    torque_reference = np.full(len(torque_array), torque_input)
    print("Torque Values: ", torque_array)

    fig, ax = plt.subplots()
    ax.plot(element, torque_array, element, torque_reference)
    ax.set(xlabel='element', ylabel='read_torque() val', title='read_torque() over instances')
    ax.set_ylim([0, 1])
    plt.show()