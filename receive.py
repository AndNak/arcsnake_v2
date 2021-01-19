import os
import can

os.system('sudo ifconfig can0 down')
os.system('sudo ip link set can0 type can bitrate 1000000')
os.system('sudo ifconfig can0 up')

can0 = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')

while True:
    try:
        msg = can0.recv(30.0)
        print(msg)
        if msg is None:
            print('No message was received')
        
    except KeyboardInterrupt:
        break

os.system('sudo ifconfig can0 down')