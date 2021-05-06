from CanMotor import CanMotor

# gear ratio is 6:1
GEAR_RATIO = 6

class CanJointMotor(CanMotor):
    def __init__(self, motor_id=0x141):
        super().__init__(GEAR_RATIO, motor_id)
    