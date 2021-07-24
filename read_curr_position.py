import os
import can
from CanJointMotor import CanJointMotor
from CanScrewMotor import CanScrewMotor
import time

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

    os.system('sudo ifconfig can1 down')
    os.system('sudo ip link set can1 type can bitrate 1000000')
    os.system('sudo ifconfig can1 up')

def cleanup():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ifconfig can1 down')

if __name__ == "__main__":
    init()

    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
    can1 = can.ThreadSafeBus(channel='can1', bustype='socketcan_ctypes')

    screw1 = CanScrewMotor(can0, 0x141)
    joint1 = CanJointMotor(can0, 0x142)
    joint2 = CanJointMotor(can0, 0x143)

    screw2 = CanScrewMotor(can1, 0x141)
    
    for _ in range(100):
        try:
            print('screw1',screw1.read_position())
            print('joint1',joint1.read_position())
            print('joint2',joint2.read_position())
            print('screw2',screw2.read_position())
        except (KeyboardInterrupt, ValueError) as e:
            print(e)

        time.sleep(0.1)

    cleanup()