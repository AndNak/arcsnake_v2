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

def profile(motor):
    profiler = Profiler()
    profiler.start()

    for i in range(1000):
        motor.pos_ctrl(0x00, 0x41, 0x00, 0x00)
        motor.read_encoder()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))

def avg(l):
    if (len(l) == 0):
        return 0

    return sum(l)/len(l)

if __name__ == "__main__":
    init()

    # make the can bus
    canBus = can.ThreadSafeBus(channel='can0', bustype='socketcan_ctypes')

    # motor initialization
    joint1 = CanJointMotor(canBus, 0x141)
    screw = CanScrewMotor(canBus, 0x143)
    utils = CanUtils()
    
    start = datetime.now()
    send_cmds_joint = []
    recv_cmds_joint = []
    send_cmds_screw = []
    recv_cmds_screw = []

    for i in range(200):
        
        try:
            time_since_start = datetime.now() - start
            
            to_vel = (math.pi**2) * math.sin(time_since_start.total_seconds() * 0.2 * math.pi)
            to_pos = (math.pi**2) * math.sin(time_since_start.total_seconds() * 0.2 * math.pi)
            
            before_send = datetime.now()
            joint1.pos_ctrl(to_pos)
            send_cmds_joint.append((before_send - datetime.now()).total_seconds())

            before_recv = datetime.now()
            joint_position = joint1.read_position()
            recv_cmds_joint.append((before_send - datetime.now()).total_seconds())

            before_send = datetime.now()
            screw.speed_ctrl(to_vel)
            send_cmds_screw.append((before_send - datetime.now()).total_seconds())

            before_recv = datetime.now()
            screw_speed = screw.read_speed()
            recv_cmds_screw.append((before_send - datetime.now()).total_seconds())

            loop_dur = datetime.now() - start - time_since_start
            # 10ms for each loop
            time.sleep(max(0, 0.01 - loop_dur.total_seconds()))
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    joint1.motor_stop()
    screw.motor_stop()

    print("avg joint send latency = %d" % (avg(send_cmds_joint)))
    print("avg joint receive latency = %d" % (avg(recv_cmds_joint)))
    print("avg screw send latency = %d" % (avg(send_cmds_screw)))
    print("avg screw receive latency = %d" % (avg(recv_cmds_screw)))

    cleanup()