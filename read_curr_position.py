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

    canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
    screw = CanScrewMotor(canBus, 0x141)
    joint1 = CanJointMotor(canBus, 0x142)
    joint2 = CanJointMotor(canBus, 0x143)
    
    for _ in range(100):
        try:
            print('screw',screw.read_position())
            print('joint1',joint1.read_position())
            print('joint2',joint2.read_position())
        except (KeyboardInterrupt, ValueError) as e:
            print(e)

        time.sleep(0.1)

    cleanup()