import os
import can
import math
from CanUtils import CanUtils

class CanMotor:
    def __init__(self):
        os.system('sudo ifconfig can0 down')
        os.system('sudo ip link set can0 type can bitrate 1000000')
        os.system('sudo ifconfig can0 up')

        self.canBus = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')
        self.utils = CanUtils()

    def send(self, arb_id, data):
        msg = can.Message(arbitration_id=arb_id, data=data, extended_id=False)
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
        msg = self.send(0x141, [0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # encoder readings are in (high byte, low byte)
        torque   = self.utils.readBytes(msg.data[3], msg.data[2])
        speed    = self.utils.readBytes(msg.data[5], msg.data[4])
        position = self.utils.readBytes(msg.data[7], msg.data[6])

        return (self.utils.encToAmp(torque), 
                self.utils.degToRad(speed), 
                self.utils.degToRad(self.utils.toDegrees(position)))

    '''
    get just the position reading from the encoder
    '''
    def read_encoder(self):
        (_, _, pos) = self.read_motor_status()
        return pos

    '''
    sends the motor to position `to_rad` by converting from radians to degrees.
    `to_rad` must be a positive value.
    actual position sent is in units of 0.01 deg/LSB (36000 == 360 deg).
    rotation direction is determined by the difference between the target pos and the current pos
    '''
    def pos_ctrl(self, to_rad):
        if (to_rad < 0 or to_rad >= 2*math.pi):
            raise ValueError("pos_ctrl: to_rad = " + str(to_rad) + ". Must be in range [0,2*pi).")
        
        # The least significant bit represents 0.01 degrees per second.
        to_deg = 100 * self.utils.radToDeg(to_rad)
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_deg)

        self.send(0x141, [0xa3, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])

    '''
    controls the speed of the motor by `to_deg` rad/s/LSB by converting from rad/s/LSB to dps/LSB.
    actual speed sent is in units of 0.01 dps/LSB.
    '''
    def speed_ctrl(self, to_rad):
        to_dps = 100 * self.utils.radToDeg(to_rad)
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_dps)
 
        msg = self.send(0x141, [0xa2, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])
        return self.utils.degToRad(self.utils.readBytes(msg.data[5], msg.data[4]))

    '''
    controls the torque current output of the motor. 
    actual control value sent is in range -2000~2000, corresponding to -32A~32A
    '''
    def torque_ctrl(self, low_byte, high_byte):
        self.send(0x141, [0xa1, 0x00, 0x00, 0x00, low_byte, high_byte,  0x00, 0x00])

    '''
    force-stops the motor.
    '''
    def motor_stop(self):
        self.send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])