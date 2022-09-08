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

def get_time(t):
    return time.time() - t

if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    screwMotor = CanUJoint(can0, 1, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    encoderMotor = CanUJoint(can0, 0, 1)
    sampling_rate = 200 # in Hz
    run_time = 5 # in second
    num_runs = 5
    
    set_num = 1
    test_num = 1
    data_fname = 'tests/ScrewTestScripts/data_files/const_torque_tests/set{0}/test{1}.csv'.format(set_num, test_num)
    command_torque = -0.6 # in amps


    try:
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed'])

            t0 = time.time()
            time.sleep(3)
            screwMotor.pos_ctrl(0, 5)
            time.sleep(20)

            
            for i in range(num_runs):
                t_i = time.time()
                while True:
                    screwMotor.torque_ctrl(command_torque)
                    row = [get_time(t0), screwMotor.read_speed(), screwMotor.read_torque()]
                    print(row)
                    test_writer.writerow(row)
                    time.sleep(1/sampling_rate)
                    if get_time(t_i) > run_time:
                        break
                    
                print('Run {0} done, put configuration back in free hang.'.format(i+1))
                for j in range(30):
                    print('Starting next run in {0} seconds'.format(30-j))
                    time.sleep(1)


    except(KeyboardInterrupt) as e:
        print(e)

    screwMotor.motor_stop() 
    encoderMotor.motor_stop()

    print('Done')

    core.CANHelper.cleanup("can0")