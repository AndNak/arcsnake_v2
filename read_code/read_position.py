from CanScrewMotor import CanScrewMotor
from CanUtils import CanUtils
import matplotlib.pyplot as plt
from datetime import datetime
import math
import os
import can
import time

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

def cleanup():
    os.system('sudo ifconfig can0 down')

if __name__ == "__main__":
    init()

    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
    screw = CanScrewMotor(can0, 0x141)
    utils = CanUtils()
    start = datetime.now()
    t = []
    x = []

    to_angle = math.pi/2
    screw.pos_ctrl(to_angle)

    for i in range(2000):
        try:
            time_since_start = datetime.now() - start
            t.append(time_since_start.total_seconds())

            position = screw.read_position()
            x.append(utils.radToDeg(position))

            loop_dur = datetime.now() - start - time_since_start
            # 10ms for each loop
            time.sleep(max(0, .1 - loop_dur.total_seconds()))
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    plt.plot(t,x,'g-')
    
    plt.xlabel('time')
    plt.ylabel('angle')
    plt.show()

    cleanup()