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


def get_time(t0):
    return time.time() - t0

if __name__ == "__main__":
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    screwMotor = CanUJoint(can0, 1, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    encoderMotor = CanUJoint(can0, 0, 1)

    sampling_rate = 200 # in Hz

    ### Change these as needed
    run_time = 30 # in second
    set_num = 1
    test_num = 1
    command_speed = -2.5 # in radians per second
    data_fname = '~/Documents/screw_test_data_files/motion_tests/set{0}/test{1}.csv'.format(set_num, test_num)

    try:
        time.sleep(3)
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed', 'torque', 'linear speed'])

            # synchronization procedure
            t0 = time.time()

            screwMotor.pos_ctrl(1.6, 6.0)
            row = [get_time(t0), screwMotor.read_speed(), screwMotor.read_torque(
            ), encoderMotor.read_speed()]
            print(row)
            test_writer.writerow(row)
            time.sleep(2)

            screwMotor.pos_ctrl(0, 6.0)
            row = [get_time(t0), screwMotor.read_speed(), screwMotor.read_torque(
            ), encoderMotor.read_speed()]
            print(row)
            test_writer.writerow(row)

            time.sleep(15)

            start_time = time.time()
            screwMotor.speed_ctrl(command_speed)
            while True:
                cur_time = time.time() - start_time
                row = [cur_time, screwMotor.read_speed(), screwMotor.read_torque(), encoderMotor.read_speed()]
                print(row)
                test_writer.writerow(row)
                time.sleep(1/sampling_rate)
                if cur_time > run_time:
                    break
    except(KeyboardInterrupt) as e:
        print(e)

    screwMotor.motor_stop()
    encoderMotor.motor_stop()

    print('Done')

    core.CANHelper.cleanup("can0")
