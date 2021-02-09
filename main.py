import os
import can
from CanMotor import CanMotor
from pyinstrument import Profiler

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

def cleanup():
    os.system('sudo ifconfig can0 down')

if __name__ == "__main__":
    init()

    screw = CanMotor()

    profiler = Profiler()
    profiler.start()

    for i in range(1000):
        screw.pos_ctrl(0x00, 0x41, 0x00, 0x00)
        screw.read_encoder()

    profiler.stop()
    print(profiler.output_text(unicode=True, color=True))

    cleanup()