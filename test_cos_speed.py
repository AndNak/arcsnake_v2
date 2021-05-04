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

    screw = CanMotor(0x142)
    joint = CanMotor()
    utils = CanUtils()
    
    start = datetime.now()
    t = []
    read_speeds = []
    set_speeds = []

    for i in range(800):
        try:
            time_since_start = datetime.now() - start
            t.append(time_since_start.total_seconds())
            
            to_vel = 4 * (math.pi**2) * math.cos(time_since_start.total_seconds() * 0.2 * math.pi)
            
            set_speeds.append(to_vel)
            screw.speed_ctrl(to_vel)
            joint.speed_ctrl(to_vel)

            (_, speed, _) = screw.read_motor_status()
            read_speeds.append(speed)

            loop_dur = datetime.now() - start - time_since_start
            # 10ms for each loop
            time.sleep(max(0, 0.01 - loop_dur.total_seconds()))
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    joint.motor_stop()
    plt.plot(t,read_speeds,'b-')
    plt.plot(t,set_speeds,'r-')
    
    plt.xlabel('time (s)')
    plt.ylabel('speed (rad/s)')
    plt.legend(["encoder speed", "set speed"])
    plt.show()

    cleanup()