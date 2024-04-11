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
    test_name = "p5s5_p1s7_p2s9_p3s8_p4s6_iter1"

    print("Trying to initialize motors")
    # joint1 = CanMotor(can0, 1, gear_ratio)
    # joint2 = CanMotor(can0, 4, gear_ratio)
    # joint3 = CanMotor(can0, 3, gear_ratio)
    # joint4 = CanMotor(can0, 6, gear_ratio)
    screw1 = CanMotor(can0, 5, 1)
    screw2 = CanMotor(can0, 7, 1)
    screw3 = CanMotor(can0, 0, 1)
    screw4 = CanMotor(can0, 8, 1)
    screw5 = CanMotor(can0, 6, 1)

    print('Motor initialization complete')
    
    # input('Press Enter to read joint current pos')
    # joint1_pos = joint1.read_multiturn_position()
    # joint2_pos = joint2.read_multiturn_position()
    # joint3_pos = joint3.read_multiturn_position()
    # joint4_pos = joint4.read_multiturn_position()

    # print('Joint 1 pos: ', joint1_pos)
    # print('Joint 2 pos: ', joint2_pos)
    # print('Joint 3 pos: ', joint3_pos)
    # print('Joint 4 pos: ', joint4_pos)

    # input('Press Enter to set joint current pos')
    # joint1.pos_ctrl(joint1_pos) # set read pos
    # joint2.pos_ctrl(joint2_pos) # set read pos
    # joint3.pos_ctrl(joint3_pos) # set read pos
    # joint4.pos_ctrl(joint4_pos) # set read pos

    # while True:
    #     try:
    #         print(screw1.read_motor_pid())
    #         Kp = 255
    #         Ki = 50
    #         screw1.override_PI_values(100, 100, Kp, Ki, 50, 50)
    #         print(screw1.read_motor_pid())
    #         break
    #     except TimeoutError:
    #         print('Timeout Error')
    #         continue
    # screwMotor.override_PI_values(100, 100, Kp, Ki, 50, 50)
    print(screw1.read_motor_pid())
    print(screw2.read_motor_pid())
    print(screw3.read_motor_pid())
    print(screw4.read_motor_pid())
    print(screw5.read_motor_pid())

    input('Press Enter to spin screw motors')

    # screw2_pos = screw2.read_multiturn_position()
    # screw2.pos_ctrl(screw2_pos) # set read pos
    # print(screw2.read_multiturn_position())
    # time.sleep(0.1)
    # screw2.pos_ctrl(screw2_pos + 0.1) # set read pos
    # print(screw2.read_multiturn_position())
    # screw2.pos_ctrl(screw2_pos + 0.2) # set read pos
    # print(screw2.read_multiturn_position())

    # screw2.speed_ctrl(5) 
    # screw2.speed_ctrl(5) 
    


    # Roll
    # screw1.speed_ctrl(5)
    # screw1.speed_ctrl(5)
    # time.sleep(0.1)
    # print(screw1.speed_ctrl(5))
    # screw2.speed_ctrl(-10)
    # time.sleep(0.1)
    # print(screw2.speed_ctrl(-10))
    # screw3.speed_ctrl(5)

    # # Torpedo
    factor = 50
    
    motor_voltages = []
    number_of_steps = 1000
    with open(f'{folder}/{test_name}.csv', 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',')

        for i in range(number_of_steps):
            voltages = []
            screw1.speed_ctrl((factor*1)*i/number_of_steps)
            screw1.clear_error_flag()
            screw2.speed_ctrl((factor*1)*i/number_of_steps)
            screw2.clear_error_flag()
            screw3.speed_ctrl((factor*1)*i/number_of_steps)
            screw3.clear_error_flag()
            screw4.speed_ctrl((factor*1)*i/number_of_steps)
            screw4.clear_error_flag()
            screw5.speed_ctrl((factor*1)*i/number_of_steps)
            screw5.clear_error_flag()

            # joint1.pos_ctrl(joint1_pos) # set read pos
            # joint2.pos_ctrl(joint2_pos) # set read pos
            # joint3.pos_ctrl(joint3_pos) # set read pos
            # joint4.pos_ctrl(joint4_pos) # set read pos

            screw1_error = screw1.read_motor_err_and_voltage()
            screw2_error = screw2.read_motor_err_and_voltage()
            screw3_error = screw3.read_motor_err_and_voltage()
            screw4_error = screw4.read_motor_err_and_voltage()
            screw5_error = screw5.read_motor_err_and_voltage()

            # joint1_error = joint1.read_motor_err_and_voltage()
            # joint2_error = joint2.read_motor_err_and_voltage()
            # joint3_error = joint3.read_motor_err_and_voltage()
            # joint4_error = joint4.read_motor_err_and_voltage()

            voltages.append(screw1_error[1])
            voltages.append(screw2_error[1])
            voltages.append(screw3_error[1])
            voltages.append(screw4_error[1])
            voltages.append(screw5_error[1])

            motor_voltages.append(voltages)

            # motor_voltages.append([screw1_error[1],
            #                     screw2_error[1]]) #, 
                                # screw3_error[1], 
                                # joint1_error[1],
                                # joint2_error[1],
                                # joint3_error[1],
                                # joint4_error[1]])

            writer.writerow(voltages)
            
            # writer.writerow([screw1_error[1], 
            #                     screw2_error[1]]) #, 
                                # screw3_error[1], 
                                # joint1_error[1],
                                # joint2_error[1],
                                # joint3_error[1],
                                # joint4_error[1]])

            # if screw1_error[2] != 0 or screw2_error[2] != 0 or screw3_error[2] != 0 or joint1_error[2] != 0 or joint2_error[2] != 0 or joint3_error[2] != 0 or joint4_error[2] != 0:
            print("Iteration: ", i)
            print("Screw 1 error: ", screw1_error)
            print("Screw 2 error: ", screw2_error)
            print("Screw 3 error: ", screw3_error)
            print("Screw 4 error: ", screw4_error)
            print("Screw 5 error: ", screw4_error)
            print('')
            # print("Joint 1 error: ", joint1_error)
            # print("Joint 2 error: ", joint2_error)
            # print("Joint 3 error: ", joint3_error)
            # print("Joint 4 error: ", joint4_error)
                # break


            time.sleep(0.01)

    print(screw1.get_error_flag())
    print(screw2.get_error_flag())
    print(screw3.get_error_flag())
    print(screw4.get_error_flag())
    print(screw5.get_error_flag())

    # # --- TESTING READ FUNCTIONS ---
    # # print error messages
    # print("Error messages:\n")
    # print("Screw 1:", screw1.read_motor_err_and_voltage(), "\n")
    # print("Screw 2:", screw2.read_motor_err_and_voltage(), "\n")
    # print("Screw 3:", screw3.read_motor_err_and_voltage(), "\n")
    # # print three-phase currents
    # print("Reading phase currents:\n")
    # print("Screw 1:", screw1.read_phase_current_data(), "\n")
    # print("Screw 2:", screw2.read_phase_current_data(), "\n")
    # print("Screw 3:", screw3.read_phase_current_data(), "\n")

    # input('Press Enter to stop motors')
    # joint1.motor_off()
    # joint2.motor_off()
    # joint3.motor_off()
    # joint4.motor_off()
    screw1.motor_off()
    screw2.motor_off()
    screw3.motor_off()
    screw4.motor_off()
    screw5.motor_off()

    print('Done')

    plt.plot(motor_voltages)
    plt.legend(["screw 5", "screw 7", "screw 9", "screw8", "screw6"]) #, "screw 3", "joint 1", "joint 2", "joint 3", "joint 4"])
    plt.title(test_name)
    plt.xlabel("time")
    plt.ylabel("Motor Voltage")
    plt.savefig(f"{folder}/{test_name}.png")
    plt.show()

    core.CANHelper.cleanup("can0")

