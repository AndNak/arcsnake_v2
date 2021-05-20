import os
import can
import math
from CanUtils import CanUtils

class CanMotor(object):
    def __init__(self, bus, gear_ratio, motor_id):
        self.canBus = bus
        self.utils = CanUtils()
        self.gear_ratio = gear_ratio
        self.id = motor_id

    def send(self, data):
        msg = can.Message(arbitration_id=self.id, data=data, extended_id=False)
        self.canBus.send(msg)
        msg = self.canBus.recv()
        return msg

    '''
    returns motor encoder readings in units of:
    torque current 
        bit range: -2048~2048 ==> real range: -33A~33A
    speed
        1 degree/s/LSB ==> 1 rad/s/LSB
    position
        14-bit range: 0~16383 deg ==> rad
    '''
    def read_motor_status(self):
        msg = self.send([0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # encoder readings are in (high byte, low byte)
        torque   = self.utils.readBytes(msg.data[3], msg.data[2])
        speed    = self.utils.readBytes(msg.data[5], msg.data[4]) / self.gear_ratio
        position = self.utils.readBytes(msg.data[7], msg.data[6]) / self.gear_ratio

        return (self.utils.encToAmp(torque), 
                self.utils.degToRad(speed), 
                self.utils.degToRad(self.utils.toDegrees(position)))

    '''
    get just the position reading from the encoder
    '''
    def read_position(self):
        (_, _, p) = self.read_motor_status()
        return p

    '''
    get just the speed reading from the encoder
    '''
    def read_speed(self):
        (_, s, _) = self.read_motor_status()
        return s
    
    '''
    get just the torque reading from the encoder
    '''
    def read_torque(self):
        (t, _, _) = self.read_motor_status()
        return t

    '''
    sends the motor to position `to_rad` by converting from radians to degrees.
    `to_rad` must be a positive value.
    actual position sent is in units of 0.01 deg/LSB (36000 == 360 deg).
    rotation direction is determined by the difference between the target pos and the current pos
    '''
    def pos_ctrl(self, to_rad, min_pos=0, max_pos=2*math.pi):
        if (to_rad < min_pos):
            # raise ValueError("pos_ctrl: to_rad = " + str(to_rad) + ". Must be in range [" \
            # + str(min_pos) + "," + str(max_pos) + ").")
            to_rad = min_pos
        
        if (to_rad >= max_pos):
            to_rad = max_pos
        
        # The least significant bit represents 0.01 degrees per second.
        to_deg = 100 * self.utils.radToDeg(to_rad)
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_deg)

        self.send([0xa3, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])

    '''
    controls the speed of the motor by `to_deg` rad/s/LSB by converting from rad/s/LSB to dps/LSB.
    actual speed sent is in units of 0.01 dps/LSB.
    '''
    def speed_ctrl(self, to_rad, max_speed=4*math.pi):
        if to_rad > max_speed:
            to_rad = max_speed

        to_dps = self.gear_ratio * 100 * self.utils.radToDeg(to_rad)
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_dps)
 
        msg = self.send([0xa2, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])
        return self.utils.degToRad(self.utils.readBytes(msg.data[5], msg.data[4]))

    '''
    controls the torque current output of the motor. 
    actual control value sent is in range -2000~2000, corresponding to -32A~32A
    '''
    def torque_ctrl(self, low_byte, high_byte):
        self.send([0xa1, 0x00, 0x00, 0x00, low_byte, high_byte, 0x00, 0x00])

    '''
    force-stops the motor.
    '''
    def motor_stop(self):
        self.send([0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])