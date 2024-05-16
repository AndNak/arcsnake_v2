### Script to actively send different motor commands. For testing whether we can overcome being stuck through clever commands.
import can
import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanScrewMotor import CanScrewMotor

if __name__ == "__main__":
    core.CANHelper.init("can0") # Intiailize can0
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan') # Create can bus object 

    motor_id = 0
    gear_ratio = 1
    testMotor = CanUJoint(can0, motor_id, gear_ratio) # Initialize motor with can bus object 
    
    print("Enter Desired Control method")
    print("1 = Position Control (Rotations)")
    print("2 = Velocity Control (Rotations Per Second)")
    print("3 = Torque Control (Amps). Range -32 to 32.")
    print("4 = Motor stop.")

    controlMethod = 0 

    controlMethod = int(input())

    try:
        while True: 
            val = float(input())
            if controlMethod == 1:
                testMotor.pos_ctrl(val * 2 * 3.14 ,2) 
            elif controlMethod == 2:
                testMotor.speed_ctrl(val * 2 * 3.14)
            elif controlMethod == 3:
                testMotor.torque_ctrl(val)
            elif controlMethod == 4:
                testMotor.motor_stop()
            else:
                raise KeyboardInterrupt

    except(KeyboardInterrupt) as e:
        print(e)

    testMotor.motor_off()

    print('Done')

    core.CANHelper.cleanup("can0")
