import os
import can

class CanMotor:
    def __init__(self):
        os.system('sudo ifconfig can0 down')
        os.system('sudo ip link set can0 type can bitrate 1000000')
        os.system('sudo ifconfig can0 up')

        self.canBus = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')

    def readBytes(self, high_byte, low_byte):
        return high_byte*256 + low_byte

    def send(self, arb_id, data):
        # can0 = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')

        msg = can.Message(arbitration_id=arb_id, data=data, extended_id=False)
        self.canBus.send(msg)
        msg = self.canBus.recv()
        return msg

    def read_encoder(self):
        msg = self.send(0x141, [0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    def pos_ctrl(low_byte, mid_byte1, mid_byte2, high_byte):
        send(0x141, [0xa3, 0x00, 0x00, 0x00, low_byte, mid_byte1, mid_byte2, high_byte])