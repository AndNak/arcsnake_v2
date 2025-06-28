import os
import can
import time
import csv
import logging
import matplotlib.pyplot as plt
import numpy as np
from scipy.signal import butter, filtfilt

import core.CANHelper
from core.CanUJoint import CanUJoint
from utils import filter_motor_data


# === Test Configuration Data ===
terrain = 'concrete' # [water, sand, concrete, gravel] *Could potentially change depending on testing!*
test_type = 'torque' # [speed, torque]  // Torque when testing statically and locking rail position, speed for dynamic testing and unlocked rail
pitch = 1 #[ , , , , ]
depth = 1 #[ , , , , ]
test_num = 1 # Trial [1 2 3]
command_speed = -10.0 #rad/s (1:1 gearbox); neg for forw and pos for back
run_time = 10 #s
sample_rate = 200 #Hz
filename = f'tests/ScrewTestScripts/motor_data_files/motor_{terrain}_tests/{test_type}_test/test{pitch}{depth}{test_num}.csv'


# === Low-Pass Filter ===
def lowpass_filter(data, cutoff=6, fs=200, order=1):
    nyq = 0.5 *fs
    normal_cutoff = cutoff / nyq
    b, a = butter(order, normal_cutoff, btype='low', analog=False)
    return filtfilt(b, a, data)

# === Basic Logging Setup ===
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# === Get Time ===
def get_time(t0):
    return time.time() - t0

def main_test():
    core.CANHelper.init('can0')
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    screwMotor = CanUJoint(can0, 0, 1, MIN_POS = 0 * 2 * np.pi, MAX_POS = 10 * 2 * np.pi)
    encoderMotor = CanUJoint(can0, 2, 1)

    logging.info(f"Current PID settings: {screwMotor.read_motor_pid()}")

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    time_data, torque_data, angular_speed_data, linear_speed_data = [], [], [], []

    try:
        t0 = time.time()
        with open(filename, mode='w', newline='') as test_data:
            writer = csv.writer(test_data)
            writer.writerow('time', 'torque', 'angular speed', 'linear speed')

            input('Ensure sensor is in free hang. Now, unbias FTS, then press Enter.')
            writer.writerow([get_time(t0)], screwMotor.read_torque(), screwMotor.read_speed(), encoderMotor.read_speed())

            input('Lower screw into medium, then press Enter.')
            writer.writerow([get_time(t0)], screwMotor.read_torque(), screwMotor.read_speed(), encoderMotor.read_speed())

            input('You can now bias the FTS sensor. Press Enter to start testing.')
            t1 = time.time()

            if test_type == 'torque':
                logging.info("Running static test: Locking encoder motor on rail.")
                ### TODO: IMPLEMENT LOGIC FOR STATIC TESTS
                encoderMotor.

            else:
                logging.info("Running dynamic test: Unlocking encoder motor on rail.")
                ### TODO: IMPLEMENT LOGIC FOR DYNAMIC TESTS
                encoderMotor.


            screwMotor.speed_ctrl(command_speed)

            while True:
                row = [get_time(t0), screwMotor.read_torque(), screwMotor.read_speed(), encoderMotor.read_speed()]
                writer.writerow(row)
                logging.debug(f"{row}")

                time_data.append(row[0])
                torque_data.append(row[1])
                angular_speed_data.append(row[2])
                linear_speed_data.append(row[3])

                time.sleep(1 / sample_rate)
                if get_time(t1) > run_time:
                    break

    except KeyboardInterrupt:
        logging.warning("Test Interrupted By User!")

    finally:
        screwMotor.motor_stop()
        encoderMotor.motor_stop()
        core.CANHelper.cleanup("can0")
        logging.info("Test Complete. Devices Are All Safetly Shut Down.")

    # === Apply Filtering ===
    filtered_torque = lowpass_filter(torque_data, fs=sample_rate)
    filtered_angular_speed = lowpass_filter(angular_speed_data, fs=sample_rate)
    filtered_linear_speed = lowpass_filter(linear_speed_data, fs=sample_rate)

    # === Plot Everything! ===
    plt.figure()
    plt.plot(time_data, filtered_torque, label="Torque")
    plt.xlabel("Time (s)"); plt.ylabel("Torque (Nm)"); plt.title("Filtered Torque"); plt.grid(True)

    plt.figure()
    plt.plot(time_data, filtered_angular_speed, label="Angular Speed")
    plt.xlabel("Time (s)"); plt.ylabel("Angular Speed (rad/s)"); plt.title("Filtered Angular Speed"); plt.grid(True)

    plt.figure()
    plt.plot(time_data, filtered_linear_speed, label="Linear Speed")
    plt.xlabel("Time (s)"); plt.ylabel("Linear Speed (m/s)"); plt.title("Filtered Linear Speed"); plt.grid(True)

    plt.show()

if __name__ == "__main__":
    main_test()