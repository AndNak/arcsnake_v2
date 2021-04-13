from CanMotor import CanMotor
from CanUtils import CanUtils
import matplotlib.pyplot as plt
from datetime import datetime

if __name__ == "__main__":
    screw = CanMotor()
    utils = CanUtils()
    start = datetime.now()
    x = []
    readvals = []
    setpoints = []

    to_val = 450
    screw.speed_ctrl(to_val)

    for i in range(5000):
        try:
            if (i % 1000 == 0):
                to_val += 100
                screw.speed_ctrl(to_val)

            time_since_start = datetime.now() - start
            x.append(time_since_start.total_seconds())

            (_, speed, _) = screw.read_motor_status()
            readvals.append(speed)
            setpoints.append(to_val)
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    plt.plot(x,readvals,'r')
    plt.plot(x,setpoints,'g')
    plt.legend(["read vals", "setpoints"], loc="upper left")
    
    plt.xlabel('time')
    plt.ylabel('speed')
    plt.show()