import os
import can
from CanJointMotor import CanJointMotor
from CanScrewMotor import CanScrewMotor

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

def cleanup():
    os.system('sudo ifconfig can0 down')

if __name__ == "__main__":
    init()

    canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
    joint1 = CanJointMotor(canBus, 0x141)
    joint2 = CanJointMotor(canBus, 0x142)
    screw = CanScrewMotor(canBus, 0x143)

    try:
        print(screw.read_encoder())
        print(joint1.read_encoder())
        print(joint2.read_encoder())
    except (KeyboardInterrupt, ValueError) as e:
        print(e)

    screw.motor_stop()
    joint1.motor_stop()
    joint2.motor_stop()

    cleanup()