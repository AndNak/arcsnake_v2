import os
import can
import math
import time
import matplotlib.pyplot as plt
from datetime import datetime
from pyinstrument import Profiler

from CanJointMotor import CanJointMotor
from CanScrewMotor import CanScrewMotor
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
    
    canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')
    # joint1 = CanJointMotor(canBus, 0x141)
    # joint2 = CanJointMotor(canBus, 0x142)
    screw = CanScrewMotor(canBus, 0x141)
    utils = CanUtils()
    
    start = datetime.now()
    t = []
    read_speeds_screw = []
    set_speeds_screw = []
    read_speeds_joint = []
    set_speeds_joint = []

    for i in range(80):
        try:
            time_since_start = datetime.now() - start
            t.append(time_since_start.total_seconds())
            
            to_vel = 5 * (math.pi**2) #* math.cos(time_since_start.total_seconds() * 0.2 * math.pi)
            # to_vel2 = (math.pi**2) * math.sin(time_since_start.total_seconds() * 0.2 * math.pi)

            set_speeds_screw.append(to_vel)
            screw.speed_ctrl(to_vel)
            (_, screw_speed, _) = screw.read_motor_status()
            # print('screw speed read: {}'.format(screw_speed))
            
            # set_speeds_joint.append(to_vel2)
            # joint1.speed_ctrl(to_vel2)
            # (_, joint_speed, _) = joint1.read_motor_status()

            read_speeds_screw.append(screw_speed)
            # read_speeds_joint.append(joint_speed)

            loop_dur = datetime.now() - start - time_since_start
            # 10ms for each loop
            time.sleep(max(0, .1 - loop_dur.total_seconds()))
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    # joint1.motor_stop()
    plt.plot(t,read_speeds_screw,'b-')
    plt.plot(t,set_speeds_screw,'r-')
    # plt.plot(t,read_speeds_joint,'g-')
    # plt.plot(t,set_speeds_joint,'y-')
    
    plt.xlabel('time (s)')
    plt.ylabel('speed (rad/s)')
    plt.legend(["screw encoder speed", "screw set speed", "joint encoder speed", "joint set speed"])
    plt.show()

    cleanup()