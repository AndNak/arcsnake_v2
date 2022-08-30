import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor
import time

from os.path import dirname, realpath  
import sys
from core.CanMotor import CanMotor
import csv
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  


if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    screwMotor = CanUJoint(can0, 1, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    encoderMotor = CanUJoint(can0, 0, 1)
    run_time = 6 # in second
    sampling_rate = 200 # in Hz

    # data_fname = '/screw_test_data_files/peak_force_tests/set1/test1.csv'
    data_fname = 'tests/ScrewTestScripts/data_files/torque_ramp_tests/test_set/test5.csv'
    initial_torque = -0.01
    final_torque = -2.0
    torque_step = -0.01
    time_step = 0.05
    num_steps = int((final_torque - initial_torque) / torque_step) + 1
    print(num_steps)

    try:
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed', 'angular position', 'interval'])
            start_time = time.time()
            
            for i in range(num_steps):

                screwMotor.torque_ctrl(initial_torque + i*torque_step)

                while True:
                    cur_time = time.time() - start_time
                    row = [cur_time, screwMotor.read_speed(), screwMotor.read_torque(), encoderMotor.read_speed(), screwMotor.read_singleturn_position(), i]
                    print(row)
                    test_writer.writerow(row)
                    time.sleep(1/sampling_rate)
                    if cur_time > time_step*(i+1):
                        break


    except(KeyboardInterrupt) as e: 
        print(e)

    screwMotor.motor_stop() 
    encoderMotor.motor_stop()

    print('Done')

    core.CANHelper.cleanup("can0")