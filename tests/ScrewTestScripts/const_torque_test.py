import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor
import time

from os.path import dirname, realpath  
import sys
from core.CanMotor import CanMotor
import csv

import matplotlib.pyplot as plt
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  

def get_time(t):
    return time.time() - t

if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    screwMotor = CanUJoint(can0, 1, 5, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    encoderMotor = CanUJoint(can0, 2, 1)
    sampling_rate = 200 # in Hz
    run_time = 5 # in second
    num_runs = 5
    
    set_num = 7
    test_num = 5
    data_fname = 'tests/ScrewTestScripts/data_files/const_torque_tests/set{0}/test{1}.csv'.format(set_num, test_num)
    command_torque = 1.5 # in amps

    time_data   = []
    torque_data = []
    angular_speed_data = []
    

    try:
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed'])

            t0 = time.time() # <-- Must be before all input()

            
            for i in range(num_runs):
                print('Run {0} done, put configuration back in free hang and Unbias the sensor'.format(i+1))
                print("Smooth the surface!")
                input('Press enter to set zero position')
                screwMotor.pos_ctrl(0, 5)
                print("Set sensor back down.")
                print("Wait a few seconds, then Bias the sensor")
                input("Press enter to continue")
                time.sleep(2)
                t_i = time.time()
                while True:
                    screwMotor.torque_ctrl(command_torque)
                    row = [get_time(t0), screwMotor.read_speed(), screwMotor.read_torque()]
                    print(row)
                    test_writer.writerow(row)

                    time_data.append(row[0])
                    angular_speed_data.append(row[1])
                    torque_data.append(row[2])

                    time.sleep(1/sampling_rate)
                    if get_time(t_i) > run_time: 
                        break
                    
                screwMotor.motor_stop()
                # for j in range(30):
                #     print('Starting next run in {0} seconds'.format(30-j))
                #     time.sleep(1)


    except(KeyboardInterrupt) as e:
        print(e)

    screwMotor.motor_stop() 
    encoderMotor.motor_stop()
    
    print('Stop log')
    print('Done')

    core.CANHelper.cleanup("can0")

    plt.figure()
    plt.plot(time_data, torque_data)
    plt.title("Torque")

    plt.figure()
    plt.plot(time_data, angular_speed_data) 
    plt.title("Angular Speed")

    plt.show()