import os
import can
from CanJointMotor import CanJointMotor
from CanScrewMotor import CanScrewMotor
import time

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')


def cleanup():
    os.system('sudo ifconfig can0 down')


if __name__ == "__main__":
    init()

    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')


    screw1 = CanScrewMotor(can0, 0x141)

    
    for _ in range(100):
        try:
            print('screw1',screw1.read_torque())

        except (KeyboardInterrupt, ValueError) as e:
            print(e)

        time.sleep(0.1)

    cleanup()