from CanMotor import CanMotor
from CanUtils import CanUtils
import matplotlib.pyplot as plt
from datetime import datetime

if __name__ == "__main__":
    screw = CanMotor()
    utils = CanUtils()
    start = datetime.now()
    x = []
    c = []

    to_angle = 539
    # The least significant bit represents 0.01 degrees per second.
    # m, l = utils.toBytes(100*to_angle)
    screw.speed_ctrl(to_angle)

    for i in range(2000):
        try:
            time_since_start = datetime.now() - start
            x.append(time_since_start.total_seconds())

            (_, _, position) = screw.read_motor_status()
            c.append(position)
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    plt.plot(x,c,'g')
    
    plt.xlabel('time')
    plt.ylabel('angle')
    plt.show()