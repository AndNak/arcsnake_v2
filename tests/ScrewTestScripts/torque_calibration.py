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

    testMotor = CanUJoint(can0, 0, 6, MIN_POS = 0 * 2 * 3.14, MAX_POS = 10 * 2 * 3.14)
    
    command_speed = 1 # in radians per second
    run_time = 10 # in seconds
    sampling_rate = 2 # in Hz
    interval = 5 # seconds
    command_torque = 0.1 # in Amps

    try:

        with open('torque_calibration_data.csv', mode='w') as test_data:
            test_writer = csv.writer(test_data, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            test_writer.writerow(['time', 'speed', 'torque', 'commanded_torque'])
            start_time = time.time()

            for i in range(1, 6):

                testMotor.torque_ctrl(command_torque * i)

                while True:
                    cur_time = time.time() - start_time
                    row = [cur_time, testMotor.read_speed(), testMotor.read_torque(), command_torque * i]
                    print(row)
                    test_writer.writerow(row)
                    time.sleep(1/sampling_rate)
                    if cur_time > interval*i:
                        break
            
    except(KeyboardInterrupt) as e:
        print(e)

    testMotor.motor_stop()

    print('Done')

    core.CANHelper.cleanup("can0")