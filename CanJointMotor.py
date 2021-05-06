from CanMotor import CanMotor
import math

# gear ratio is 6:1
GEAR_RATIO = 6
MIN_POS = 0
MAX_POS = 2*math.pi

class CanJointMotor(CanMotor):
    def __init__(self, motor_id=0x141):
        super(CanJointMotor, self).__init__(GEAR_RATIO, motor_id)

    def pos_ctrl(self, to_rad):
        super(CanJointMotor, self).pos_ctrl(to_rad, MIN_POS, MAX_POS)