import os
import can

os.system('sudo ifconfig can1 down')
os.system('sudo ip link set can1 type can bitrate 1000000')
os.system('sudo ifconfig can1 up')

can1 = can.interface.Bus(channel='can1', bustype='socketcan_ctypes')

msg = can.Message(arbitration_id=0x141, data = [0x9a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], extended_id = False)
can1.send(msg)

os.system('sudo ifconfig can1 down')