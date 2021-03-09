from CanMotor import CanMotor
from CanUtils import CanUtils
import matplotlib.pyplot as plt
from datetime import datetime

if __name__ == "__main__":
    screw = CanMotor()
    utils = CanUtils()
    start = datetime.now()
    x = []
    # a = []
    b = []
    # c = []

    to_val = 539
    # The least significant bit represents 0.01 degrees per second.
    m, l = utils.writeBytes(100*to_val)
    screw.speed_ctrl(l, m, 0, 0)

    for i in range(5000):
        try:
            time_since_start = datetime.now() - start
            x.append(time_since_start.total_seconds())

            (torque, speed, position) = screw.read_motor_status()
            # y.append(screw.read_encoder())
            # a.append(torque)
            b.append(speed)
            # c.append(position)
        except KeyboardInterrupt or ValueError:
            break

    screw.motor_stop()
    # plt.plot(x,a,'b')
    plt.plot(x,b,'r')
    # plt.plot(x,c,'g')
    
    plt.xlabel('time')
    plt.ylabel('speed')
    plt.show()