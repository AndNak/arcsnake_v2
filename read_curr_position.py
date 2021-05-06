import os
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

    joint1 = CanJointMotor(0x141)
    joint2 = CanJointMotor(0x142)
    screw = CanScrewMotor(0x143)

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