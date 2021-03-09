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

    def read_encoder(self):
        msg = self.send(0x141, [0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        # encoder current position: msg.data[3] == high byte, msg.data[2] == low byte
        # return self.utils.toDegrees(self.utils.readBytes(msg.data[3], msg.data[2]))
        return (self.utils.readBytes(msg.data[3], msg.data[2]))

    def pos_ctrl(self, to_angle):
        # The least significant bit represents 0.01 degrees per second.
        m, l = self.utils.writeBytes(100*to_angle)
        if (m < 0 or m >= 256 or l < 0 or l >= 256):
            raise ValueError("to_angle = " + str(to_angle) + ": Must be in range [0,65535]")

        self.send(0x141, [0xa3, 0x00, 0x00, 0x00, l, m, 0, 0])

    def speed_ctrl(self, low_byte, mid_byte1, mid_byte2, high_byte):
        self.send(0x141, [0xa2, 0x00, 0x00, 0x00, low_byte, mid_byte1, mid_byte2, high_byte])

    def torque_ctrl(self, low_byte, high_byte):
        self.send(0x141, [0xa1, 0x00, 0x00, 0x00, low_byte, high_byte, 0x00, 0x00])

    def read_motor_status(self):
        msg = self.send(0x141, [0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        torque = self.utils.readBytes(msg.data[3], msg.data[2])
        speed = self.utils.readBytes(msg.data[5], msg.data[4])
        position = self.utils.readBytes(msg.data[7], msg.data[6])
        return (torque, speed, position)

    def motor_stop(self):
        self.send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])