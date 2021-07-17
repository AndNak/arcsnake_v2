'''
from CanMotor import CanMotor
from CanUtils import CanUtils
import matplotlib.pyplot as plt
from datetime import datetime
import math

if __name__ == "__main__":
    screw = CanMotor()
    utils = CanUtils()
    start = datetime.now()
    x = []
    c = []

    to_angle = math.pi/2
    screw.pos_ctrl(to_angle)

    for i in range(2000):
        try:
            time_since_start = datetime.now() - start
            x.append(time_since_start.total_seconds())

            position = screw.read_encoder()
            c.append(utils.radToDeg(position))
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    plt.plot(x,c,'go')
    
    plt.xlabel('time')
    plt.ylabel('angle')
    plt.show()
    '''