from CanMotor import CanMotor
from CanUtils import CanUtils
import matplotlib.pyplot as plt
from datetime import datetime
import math

if __name__ == "__main__":
    screw = CanMotor()
    utils = CanUtils()
    screw.pos_ctrl(0)

    for i in range(5):
        try:
            position = screw.read_encoder()
            print(position)
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()