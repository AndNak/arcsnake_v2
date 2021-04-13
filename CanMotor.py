import os
import can
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
        bit range: -2048~2048
        real range: -33A~33A
    speed
        1 degree/s/LSB
    position
        14-bit range: 0~16383
    '''
    def read_motor_status(self):
        msg = self.send(0x141, [0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

        # encoder readings are in (high byte, low byte)
        torque   = self.utils.readBytes(msg.data[3], msg.data[2])
        speed    = self.utils.readBytes(msg.data[5], msg.data[4])
        position = self.utils.readBytes(msg.data[7], msg.data[6])

        return (torque, speed, position)

    '''
    get just the position reading from the encoder
    '''
    def read_encoder(self):
        (_, _, pos) = self.read_motor_status()
        return pos

    def pos_ctrl(self, to_angle):
        # The least significant bit represents 0.01 degrees per second.
        byte1, byte2, byte3, byte4 = self.utils.toBytes(100*to_angle)
        if (byte1 < 0 or byte1 >= 256):
            raise ValueError("ValueError: to_angle = " + str(100*to_angle) + ": Must be in range [0,16777216]")

        self.send(0x141, [0xa3, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])

    def speed_ctrl(self, to_val):
        byte1, byte2, byte3, byte4 = self.utils.toBytes(100*to_val)

        if (byte1 < 0 or byte1 >= 256):
            raise ValueError("ValueError: to_val = " + str(100*to_val) + ": Must be in range [0,16777216]")
        
        self.send(0x141, [0xa2, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])

    def torque_ctrl(self, low_byte, high_byte):
        self.send(0x141, [0xa1, 0x00, 0x00, 0x00, low_byte, high_byte,  0x00, 0x00])

    def motor_stop(self):
        self.send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])