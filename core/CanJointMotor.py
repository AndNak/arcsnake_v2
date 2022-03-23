from .CanMotor import CanMotor
import math

# gear ratio is 12:1
GEAR_RATIO = 6
MIN_POS = 0
MAX_POS = 2*math.pi

class CanJointMotor(CanMotor):
    def __init__(self, bus, motor_id):
        super(CanJointMotor, self).__init__(bus, GEAR_RATIO, motor_id)

    def pos_ctrl(self, to_rad):
        return super(CanJointMotor, self).pos_ctrl(to_rad, MIN_POS, MAX_POS)