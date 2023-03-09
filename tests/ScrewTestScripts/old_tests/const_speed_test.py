import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor
import time
import numpy as np

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

    screwMotor = CanUJoint(can0, 5, 1, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    # encoderMotor = CanUJoint(can0, 2, 1)


    sampling_rate = 200 # in Hz

    ### Change these as needed
    run_time = 15 # in second
    set_num = 4
    test_num = 7
    command_speed = -12.0 # in radians per second
    Kp = 255
    Ki = 50
    test_name = 'screw5maxed_Kp{0}_Ki{1}_v{2}_noshell'.format(Kp, Ki, int(-command_speed))
    data_fname = 'tests/ScrewTestScripts/data_files/speed_pi_control/{0}'.format(test_name)

    time_data   = []
    torque_data = []
    angular_speed_data = []
    linear_speed_data = []

    print(screwMotor.read_motor_pid())
    screwMotor.override_PI_values(100, 100, Kp, Ki, 50, 50)
    print(screwMotor.read_motor_pid())
    
    try:
        
        t0 = time.time()
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed'])

            # # synchronization procedure
            # print('Sensor should be in free hang. UNBIAS SENSOR')
            # print("Smooth the surface!")
            # input('Press enter to set zero position')
            # screwMotor.pos_ctrl(0, 8)
            # print("Set sensor back down.")
            # print("Wait a few seconds, then Bias the sensor")
            # input("Press enter to continue")

            t1 = time.time()
            screwMotor.speed_ctrl(command_speed)
            while True:
                row = [get_time(t0), abs(screwMotor.read_speed()), abs(screwMotor.read_torque()), 0]
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

    screwMotor.motor_stop()
    # encoderMotor.motor_stop()

    print('Done, stop sensor log')

    core.CANHelper.cleanup("can0")


    plt.figure()
    plt.plot(time_data, torque_data)
    plt.plot(time_data, angular_speed_data)
    plt.title("Screw 5, Kp = {0}, Ki = {1}, Set Vel = {2}, No Shell".format(Kp, Ki, abs(command_speed)))
    plt.legend(['Torque', 'Angular Speed'])
    # plt.ylim([0, 20])
    # plt.yticks(np.linspace(0, 20, 11))
    plt.savefig('tests/ScrewTestScripts/data_files/speed_pi_control/{0}.png'.format(test_name))
    plt.show()