from CanMotor import CanMotor
import math

MAX_SPEED = 4*math.pi
# gear ratio is 1:1
GEAR_RATIO = 1

class CanScrewMotor(CanMotor):
    def __init__(self, bus, motor_id):
        super(CanScrewMotor, self).__init__(bus, GEAR_RATIO, motor_id)

    def speed_ctrl(self, to_rad):
        return super(CanScrewMotor, self).speed_ctrl(to_rad, MAX_SPEED)