from CanJointMotor import CanJointMotor
from CanScrewMotor import CanScrewMotor

if __name__ == "__main__":
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