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
    
    

    controlMethod = 0 


    try:
        while True:
            print("Enter Desired Control method")
            print("1 = Position Control (Rotations)")
            print("2 = Velocity Control (Rotations Per Second)")
            print("3 = Torque Control (Amps). Range -32 to 32.")
            print("4 = Motor stop.")
            print("5 = Motor start.")
            print("6 = Motor off.")
            print("Ctrl + C to quit")
            controlMethod = int(input("Select Control Method: "))
            if controlMethod == 1:
                val = float(input("Select position in rotations: "))
                testMotor.pos_ctrl(val * 2 * 3.14 ,2) 
                print(f"Commanding position to {val} rotations.")
            elif controlMethod == 2:
                val = float(input("Select velocity in rotations per second: "))
                testMotor.speed_ctrl(val * 2 * 3.14)
                print(f"Commanding velocity to {val} rotations per second.")
            elif controlMethod == 3:
                val = float(input("Select torque in amps (-32, 32): "))
                testMotor.torque_ctrl(val)
                print(f"Commanding torque to {val} Amps")
            elif controlMethod == 4:
                testMotor.motor_stop()
                print("Commanding motor stop.")
            elif controlMethod == 5:
                testMotor.motor_start()
                print("Commanding motor start.")
            elif controlMethod == 6:
                testMotor.motor_off()
                print("Commanding motor off.")
            else:
                raise KeyboardInterrupt

    except(KeyboardInterrupt) as e:
        print(e)

    testMotor.motor_off()

    print('Done')

    core.CANHelper.cleanup("can0")
