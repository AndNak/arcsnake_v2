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

    screwMotor1 = CanUJoint(can0, 1, 5, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    screwMotor2 = CanUJoint(can0, 2, 5, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    encoderMotor = CanUJoint(can0, 0, 1)
    sampling_rate = 200 # in Hz
    run_time = 30 # in second
    data_fname = '~/Documents/screw_test_data_files/motion_tests/set1/test1.csv'
    command_speed = -2.5 # in radians per second

    try:
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed'])
            screwMotor1.speed_ctrl(command_speed)
            screwMotor2.speed_ctrl(command_speed)
            start_time = time.time()
            while True:
                cur_time = time.time() - start_time
                row = [cur_time, screwMotor1.read_speed(), screwMotor1.read_torque(), encoderMotor.read_speed()]
                print(row)
                test_writer.writerow(row)
                time.sleep(1/sampling_rate)
                if cur_time > run_time:
                    break
    except(KeyboardInterrupt) as e:
        print(e)

    screwMotor1.motor_stop() 
    encoderMotor.motor_stop()

    print('Done')

    core.CANHelper.cleanup("can0")