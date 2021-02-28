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
        data = msg.data

        new_pos = self.utils.readBytes(data[3], data[2])
        return self.utils.toDegrees(new_pos)

    def pos_ctrl(self, to_angle):
        if (to_angle < 0 or to_angle >= 256):
            raise ValueError("to_angle = " + str(to_angle) + ": Must be in range [0,255]")

        # The least significant bit represents 0.01 degrees per second.
        m, l = self.utils.writeBytes(100*to_angle)
        self.send(0x141, [0xa3, 0x00, 0x00, 0x00, l, m, 0, 0])

    def speed_ctrl(self, low_byte, mid_byte1, mid_byte2, high_byte):
        self.send(0x141, [0xa2, 0x00, 0x00, 0x00, low_byte, mid_byte1, mid_byte2, high_byte])

    def motor_stop(self):
        self.send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])