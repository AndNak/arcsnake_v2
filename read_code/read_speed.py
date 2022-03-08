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
    readspeed = []
    readpos = []
    setpoints = []
    returnspeeds = []

    to_val = 1680#math.pi*6
    print(str(to_val))
    returnspeed = screw.speed_ctrl(to_val)

    for i in range(5000):
        try:
            # if (i % 500 == 0):
        #         to_val += math.pi
        #         print(str(to_val))
            returnspeed = screw.speed_ctrl(to_val)

            time_since_start = datetime.now() - start
            x.append(time_since_start.total_seconds())

            (_, speed, pos) = screw.read_motor_status()
            readspeed.append(speed)
            readpos.append(pos)
            returnspeeds.append(returnspeed*2)
            setpoints.append(to_val)
        except (KeyboardInterrupt, ValueError) as e:
            print(e)
            break

    screw.motor_stop()
    plt.plot(x,readspeed,'r')
    # plt.plot(x,readpos,'b')
    plt.plot(x,setpoints,'g')
    plt.plot(x,returnspeeds,'y')
    plt.legend(["read speed", "setpoints", "return speeds"], loc="upper left")
    
    plt.xlabel('time')
    plt.ylabel('speed')
    plt.show()