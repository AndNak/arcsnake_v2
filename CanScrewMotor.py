from CanMotor import CanMotor
import math

MAX_SPEED = 4*math.pi
# gear ratio is 6:1
GEAR_RATIO = 1

class CanScrewMotor(CanMotor):
    def __init__(self, motor_id=0x141):
        super().__init__(GEAR_RATIO, motor_id)

    '''
    controls the speed of the motor by `to_deg` rad/s/LSB by converting from rad/s/LSB to dps/LSB.
    actual speed sent is in units of 0.01 dps/LSB.
    '''
    def speed_ctrl(self, to_rad):
        if to_rad > MAX_SPEED:
            to_rad = MAX_SPEED

        to_dps = 100 * self.utils.radToDeg(to_rad)
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_dps)
 
        msg = self.send([0xa2, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])
        return self.utils.degToRad(self.utils.readBytes(msg.data[5], msg.data[4]))