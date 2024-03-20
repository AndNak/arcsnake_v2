import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor
import time
import numpy as np
from core.timeout import TimeoutError

import os
from os.path import dirname, realpath
import sys
from core.CanMotor import CanMotor
import csv

import matplotlib.pyplot as plt

arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  


def get_time(t0):
    return time.time() - t0

if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')
    while True:
        try:
            print("Trying to initialize motors")
            screwMotor = CanMotor(can0, motor_id=0, gear_ratio=1)
            break
        except TimeoutError:
            print('Timeout Error')
            continue
        # screwMotor = CanUJoint(can0, 5, 1, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    # encoderMotor = CanUJoint(can0, 2, 1)

    sampling_rate = 200 # in Hz
    ### Change these as needed
    run_time = 5 # in seconds
    set_num = 4
    test_num = 7
    # speed, in radians per second
    # command_speed = -20.0 
    # command_speed = -1.0     # low
    # command_speed = -10.0    # mid
    command_speed = -50.0    # high
    Kp = 255
    Ki = 50
    # test_name = 'block_test_trial_01' #new block, low tension, low speed
    # test_name = 'block_test_trial_02' #new block, low tension, mid speed
    # test_name = 'block_test_trial_03' #new block, low tension, hi  speed
    # test_name = 'block_test_trial_04' #new block, hi  tension, low speed
    # test_name = 'block_test_trial_05' #new block, hi  tension, mid speed
    # test_name = 'block_test_trial_06' #new block, hi  tension, hi  speed
    # test_name = 'block_test_trial_07' #old block, hi  tension, low speed
    # test_name = 'block_test_trial_08' #old block, hi  tension, mid speed
    test_name = 'block_test_trial_09' #old block, hi  tension, hi  speed
    data_folder = "tests/System Tests/SystemTest_datafiles/screwDriveTrainTests"

    time_data   = []
    torque_data = []
    angular_speed_data = []
    linear_speed_data = []

    while True:
        try:
            print(screwMotor.read_motor_pid())
            screwMotor.override_PI_values(100, 100, Kp, Ki, 50, 50)
            print(screwMotor.read_motor_pid())
            break
        except TimeoutError:
            print('Timeout Error')
            continue
    screwMotor.override_PI_values(100, 100, Kp, Ki, 50, 50)
    
    screwMotor.speed_ctrl(command_speed)
    screwMotor.speed_ctrl(command_speed)
    try:
        
        t0 = time.time()
        with open(os.path.join(data_folder, test_name + "_csv.csv"), mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed'])

            t1 = time.time()
            while True:
            #     while True:
            #         try:
                row = [get_time(t0), abs(screwMotor.read_speed()), abs(screwMotor.read_torque()), 0]
                    #     break
                    # except TimeoutError:
                    #     print('Timeout Error')
                    #     continue
                print(row)
                test_writer.writerow(row)

                time_data.append(row[0])
                angular_speed_data.append(row[1])
                torque_data.append(row[2])
                linear_speed_data.append(row[3])


                time.sleep(1/sampling_rate)
                if get_time(t1) > run_time:
                    break
    except(KeyboardInterrupt) as e:
        print(e)

    # while True:
    #     try:
    screwMotor.motor_stop()
        #     break
        # except TimeoutError:
        #     print('Timeout Error')
        #     continue
    # encoderMotor.motor_stop()

    print('Done, stop sensor log')

    core.CANHelper.cleanup("can0")


    plt.figure()
    plt.plot(time_data, torque_data)
    plt.plot(time_data, angular_speed_data)
    plt.title(test_name)
    plt.legend(['Torque', 'Angular Speed'])
    # plt.ylim([0, 20])
    # plt.yticks(np.linspace(0, 20, 11))
    plt.savefig(os.path.join(data_folder, test_name + "_plot.png"))
    plt.show()