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
    t0 = time.time()
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    screwMotor1 = CanUJoint(can0, 0, 5, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    screwMotor2 = CanUJoint(can0, 1, 5, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    encoderMotor = CanUJoint(can0, 2, 1)
    sampling_rate = 200 # in Hz

    run_time = 30 # in second
    set_num = 1
    test_num = 6
    command_speed = 2.0 # in radians per second
    data_fname = 'tests/ScrewTestScripts/data_files/doublescrew_tests/set{0}/test{1}.csv'.format(set_num, test_num)

    try:
        t0 = time.time()
        with open(data_fname, mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'angular speed 1', 'angular speed 2', 'torque 1', 'torque 2', 'linear speed', 'linear position (meters)'])

            # # synchronization procedure
            screwMotor1.pos_ctrl(0, 5.0)
            screwMotor2.pos_ctrl(0, 5.0)

            input('Press Enter to start trial')

            ### Start main trial loop
            t1 = time.time()
            screwMotor1.speed_ctrl(-command_speed)
            screwMotor2.speed_ctrl(command_speed)
            encoderMotor.torque_ctrl(6)
            while True:
                row = [get_time(t0), screwMotor1.read_speed(), screwMotor2.read_speed(), screwMotor1.read_torque(), screwMotor2.read_torque(), encoderMotor.read_speed(), encoderMotor.read_multiturn_position() *-.09525/2]
                print(row[6])
                test_writer.writerow(row)
                time.sleep(1/sampling_rate)
                if get_time(t1) > run_time:
                    break
                
    except(KeyboardInterrupt) as e:
        print(e)

    screwMotor1.motor_stop() 
    screwMotor2.motor_stop()
    encoderMotor.motor_stop()

    print('Done')

    core.CANHelper.cleanup("can0")
 