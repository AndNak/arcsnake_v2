import os
import can

os.system('sudo ifconfig can0 down')
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ifconfig can0 up')

send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
