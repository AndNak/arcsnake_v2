from CanMotor import CanMotor

class CanJointMotor(CanMotor):
    def __init__(self, motor_id=0x141):
        super().__init__(1, motor_id)

    