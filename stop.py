import os
import can

os.system('sudo ifconfig can0 down')
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ifconfig can0 up')

data = [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]

canBus = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')

msg = can.Message(arbitration_id=0x141, data=data, extended_id=False)
canBus.send(msg)