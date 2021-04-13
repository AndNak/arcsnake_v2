import os
import can
import math
import time
import matplotlib.pyplot as plt
from datetime import datetime
from pyinstrument import Profiler

from CanMotor import CanMotor
from CanUtils import CanUtils

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

def cleanup():
    os.system('sudo ifconfig can0 down')

def profile(screw):
    profiler = Profiler()
    profiler.start()

    for i in range(1000):
        screw.pos_ctrl(0x00, 0x41, 0x00, 0x00)
        screw.read_encoder()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))

if __name__ == "__main__":
    init()

    screw = CanMotor()
    utils = CanUtils()
    
    start = datetime.now()
    x = []
    y = []
    z = []

    for i in range(400):
    # while (True):
        try:
            time_since_start = datetime.now() - start
            x.append(time_since_start.total_seconds())
            
            amp = 30.0
            freq = 0.1
            to_angle = 40+amp * math.sin(time_since_start.total_seconds() * freq * math.pi)
            
            z.append(to_angle)
            screw.pos_ctrl(to_angle)

            # y.append(utils.toDegrees(utils.readBytes(m,l)))
            y.append(screw.read_encoder())

            loop_dur = datetime.now() - start - time_since_start
            # 10ms for each loop
            time.sleep(max(0, 0.01 - loop_dur.total_seconds()))
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    plt.plot(x,y,'b-')
    plt.plot(x,z,'r-')
    
    plt.xlabel('time')
    plt.ylabel('angle')
    plt.legend(["encoder angle", "set angle"])
    plt.show()

    cleanup()