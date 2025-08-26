from core.CanMotorNew import CanMotor
from core.MotorListener import MotorListener
import core.CANHelper
import can
import time
"""
Script for modular/system testing of ARCSnake
"""
### Initialize single/multiple listeners/notifiers
def init_listen_notify(can_thread, motors):
    input("Start listenter and notifier")
    listener = MotorListener(motors)
    notifier = can.Notifier(can_thread, [listener])
    return listener, notifier

### Single/Multiple motor tests with modulaity
def init_motors(motors):
	input("Initialize motor(s)")
	for motor in motors:
		motor.initialize_motor()

### Functionality for getting position reading for motion profiles
def set_motion_profile(motors): # Use on U-Joint motors only
	target_positions = []
	input("Set desired motion profile for ARCSnake")
	for motor in motors:
		motor.read_multiturn_periodic()
		motor_data = motor.motor_data
		target_positions.append(motor_data.multiturn_position)
	return target_positions
		
### Postion control
def position_control(motors, target_position): # Set motor to hold position of target_position
    input("Start position control")
    for idx, motor in enumerate(motors):
        motor.initialize_control_command()
        motor.set_control_mode("position", target_position[idx])
    return

### Speed control
def speed_control(motors, target_speed, mode): # Use on screw shell motors only
    input("Start speed control")
    if mode == "tunnel":
        for idx, motor in enumerate(motors):
            motor.initialize_control_command()
            if idx % 2 == 0: # Reverse direction for certain motors, must pay attention to order in motor list
                motor.set_control_mode("speed", -target_speed)
            else:
                motor.set_control_mode("speed", target_speed)
    
    elif mode == "straight":
        for idx, motor in enumerate(motors):
            motor.initialize_control_command()
            if idx == 3: # Reverse direction for certain motors, must pay attention to order in motor list
                motor.set_control_mode("speed", -target_speed)
            else:
                motor.set_control_mode("speed", target_speed)

    return

### Print motor data
def print_motor_data(motors): # Can add debugging functionality for each motor
    for idx, motor in enumerate(motors):
        print("Motor: ", idx)
        print(motor.motor_data, "-" * 40)
    time.sleep(0.25)  # Delay after printing all motors
    return

### Send periodic status updates
def start_send(motors):
    input("Start periodic sends")
    for motor in motors:
        motor.read_status_periodic()
        motor.read_multiturn_periodic()
        motor.read_motor_state_periodic()
    return

### Stop motors and clean up CAN line
def stop_motors(can_thread, motors):
    for motor in motors:
        motor.stop_all_custom_periodic()
        motor.motor_off()

    core.CANHelper.cleanup("can0")
    can_thread.shutdown()
    print("Exiting")
    exit(0)
    return

if __name__ == "__main__":
    # Initialize CAN bus
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    ### Screw shell motors (24V)
    screw_head_end = CanMotor(can0, motor_id = 3, gear_ratio = 5) # CHECK GEAR RATIO
    screw_head_mid = CanMotor(can0, motor_id = 4, gear_ratio = 5)
    screw_tail_mid = CanMotor(can0, motor_id = 1, gear_ratio = 5)
    screw_tail_end = CanMotor(can0, motor_id = 0, gear_ratio = 5)
    screw_motors = [screw_head_end, screw_head_mid, screw_tail_mid, screw_tail_end]

    ### U-joint motors (51V)
    # U-joints pointing head to tail, with segement location
    joint_h2t_head = CanMotor(can0, motor_id = 7, gear_ratio = 1) # CHECK GEAR RATIO
    joint_h2t_mid = CanMotor(can0, motor_id = 6, gear_ratio = 1)
    joint_h2t_tail = CanMotor(can0, motor_id = 5, gear_ratio = 1)

    # U-joints pointing tail to head, with segement location
    joint_t2h_head = CanMotor(can0, motor_id = 9, gear_ratio = 1)
    joint_t2h_mid = CanMotor(can0, motor_id = 10, gear_ratio = 1)
    joint_t2h_tail = CanMotor(can0, motor_id = 8, gear_ratio = 1)
    joint_motors = [joint_h2t_head, joint_h2t_mid, joint_h2t_tail,
                     joint_t2h_head, joint_t2h_mid, joint_t2h_tail]

    all_motors = screw_motors + joint_motors  # Combine all motors into one list
    
    # head_screw_motors = [screw_head_end, screw_head_mid]  # Test screw motors
    # head_joint_motors = [joint_h2t_head, joint_h2t_mid, joint_t2h_head]

    # tail_screw_motors = [screw_tail_mid, screw_tail_end]
    # tail_joint_motors = [joint_h2t_tail, joint_t2h_mid, joint_t2h_tail]

    # head_all = head_screw_motors + head_joint_motors
    # tail_all = tail_screw_motors + tail_joint_motors
    #test = [screw_tail_mid]
    # Head end CW
    # Head mid CW
    # Tail mid CW
    # Tail end CCW


    try:
        listener, notifier = init_listen_notify(can0, all_motors)  # Initialize listener and notifier
        # listener, notifier = init_listen_notify(can0, test_all)
        # listener, notifier = init_listen_notify(can0, test)
        # ### Start sequence
        init_motors(all_motors)  # Initialize all motors
        start_send(all_motors)  # Start periodic sends for all motors
        ### Periodic send needed after initialization????
        # init_motors(test)  # Initialize test motors
        # start_send(test)  # Start periodic sends for test motors


        target_positions = set_motion_profile(joint_motors)  # Set motion profile for U-joint motors
        # target_positions = set_motion_profile(tail_joint_motors)  # Set motion profile for test motors
        # print(target_positions)

        target_speed = 2
        position_control(joint_motors, target_positions)
        # screw_tail_mid.initialize_control_command()
        # screw_tail_mid.set_control_mode("speed", target_speed)
        speed_control(screw_motors, target_speed, "straight")  # Set screw shell motors to speed control
        """
        target_speed = 5
        position_control(joint_motors, target_positions)  # Set U-joint motors to hold position
        speed_control(screw_motors, target_speed)  # Set screw shell motors to speed control
        """
        while True:
            print_motor_data(all_motors)
            # print_motor_data(test)

    except Exception as e:
        print("Error occurred:", e)
    except KeyboardInterrupt:
        print("Keyboard interrupt detected.")
    finally:
        stop_motors(can0, all_motors)  # Stop all motors and shutdown CAN bus
        # stop_motors(can0, test)  # Stop test motors and shutdown CAN bus
    """
    while True:
    print("1. Print motor data\n2. Run position control\n3. Run speed control\n4. Stop and exit")
    choice = input("Select an option: ")
    if choice == "1":
        print_motor_data(all_motors)
    elif choice == "2":
        position_control(joint_motors, target_positions)
    elif choice == "3":
        speed_control(screw_motors, target_speed)
    elif choice == "4":
        stop_motors(can0, all_motors)
        break
    """