from core.CanMotorNew import CanMotor
from core.MotorListener import MotorListener
from core.MotionProfiles import ARCSnakeMotionController, create_safe_motion_profile
from core.SnakeLocomotion import SnakeLocomotionController
import core.CANHelper
import can
import time
import sys

"""
Interactive Script for modular/system testing of ARCSnake
Allows user to select modes, speeds, and test individual motors without editing code
"""

### Initialize single/multiple listeners/notifiers
def init_listen_notify(can_thread, motors):
    print("Starting listener and notifier...")
    listener = MotorListener(motors)
    notifier = can.Notifier(can_thread, [listener])
    return listener, notifier

### Single/Multiple motor tests with modularity
def init_motors(motors):
    print("Initializing motor(s)...")
    for motor in motors:
        motor.initialize_motor()

### Functionality for getting position reading for motion profiles
def set_motion_profile(motors): # Use on U-Joint motors only
    target_positions = []
    print("Setting motion profile for ARCSnake...")
    for motor in motors:
        motor.read_multiturn_periodic()
        motor_data = motor.motor_data
        target_positions.append(motor_data.multiturn_position)
    return target_positions
        
### Position control
def position_control(motors, target_position): # Set motor to hold position of target_position
    print("Starting position control...")
    for idx, motor in enumerate(motors):
        motor.initialize_control_command()
        motor.set_control_mode("position", target_position[idx])
    return

### Speed control
def speed_control(motors, target_speed, mode): # Use on screw shell motors only
    print(f"Starting speed control with mode: {mode}")
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
    print("Starting periodic sends...")
    for motor in motors:
        motor.read_status_periodic()
        motor.read_multiturn_periodic()
        motor.read_motor_state_periodic()
    return

### Stop motors and clean up CAN line
def stop_motors(can_thread, motors):
    print("Stopping motors and cleaning up...")
    for motor in motors:
        motor.stop_all_custom_periodic()
        motor.motor_off()

    core.CANHelper.cleanup("can0")
    can_thread.shutdown()
    print("Exiting")
    return

def print_motor_info():
    """Print information about available motors"""
    print("\n" + "="*60)
    print("MOTOR INFORMATION:")
    print("="*60)
    print("SCREW SHELL MOTORS (24V):")
    print("  - screw_head_end (ID: 3, Gear Ratio: 5)")
    print("  - screw_head_mid (ID: 4, Gear Ratio: 5)")
    print("  - screw_tail_mid (ID: 1, Gear Ratio: 5)")
    print("  - screw_tail_end (ID: 0, Gear Ratio: 5)")
    print("\nU-JOINT MOTORS (51V):")
    print("  - joint_h2t_head (ID: 7, Gear Ratio: 1) - Head to tail")
    print("  - joint_h2t_mid (ID: 6, Gear Ratio: 1) - Head to tail")
    print("  - joint_h2t_tail (ID: 5, Gear Ratio: 1) - Head to tail")
    print("  - joint_t2h_head (ID: 9, Gear Ratio: 1) - Tail to head")
    print("  - joint_t2h_mid (ID: 10, Gear Ratio: 1) - Tail to head")
    print("  - joint_t2h_tail (ID: 8, Gear Ratio: 1) - Tail to head")
    print("="*60)

def get_motor_selection():
    """Get user selection for which motors to test"""
    print("\nMOTOR SELECTION:")
    print("1. All motors")
    print("2. Screw motors only")
    print("3. U-joint motors only")
    print("4. Head motors only (screw_head_end, screw_head_mid, joint_h2t_head, joint_t2h_head)")
    print("5. Tail motors only (screw_tail_mid, screw_tail_end, joint_h2t_tail, joint_t2h_tail)")
    print("6. Individual motor")
    
    while True:
        try:
            choice = int(input("Select motor group (1-6): "))
            if 1 <= choice <= 6:
                return choice
            else:
                print("Please enter a number between 1 and 6")
        except ValueError:
            print("Please enter a valid number")

def get_individual_motor():
    """Get user selection for individual motor"""
    print("\nINDIVIDUAL MOTOR SELECTION:")
    print("Screw motors:")
    print("  1. screw_head_end (ID: 3)")
    print("  2. screw_head_mid (ID: 4)")
    print("  3. screw_tail_mid (ID: 1)")
    print("  4. screw_tail_end (ID: 0)")
    print("U-joint motors:")
    print("  5. joint_h2t_head (ID: 7)")
    print("  6. joint_h2t_mid (ID: 6)")
    print("  7. joint_h2t_tail (ID: 5)")
    print("  8. joint_t2h_head (ID: 9)")
    print("  9. joint_t2h_mid (ID: 10)")
    print("  10. joint_t2h_tail (ID: 8)")
    
    while True:
        try:
            choice = int(input("Select individual motor (1-10): "))
            if 1 <= choice <= 10:
                return choice
            else:
                print("Please enter a number between 1 and 10")
        except ValueError:
            print("Please enter a valid number")

def get_speed_mode():
    """Get user selection for speed control mode"""
    print("\nSPEED CONTROL MODE:")
    print("1. Tunnel mode (alternate direction for even/odd motors)")
    print("2. Straight mode (reverse direction for motor ID 3)")
    
    while True:
        try:
            choice = int(input("Select mode (1-2): "))
            if choice == 1:
                return "tunnel"
            elif choice == 2:
                return "straight"
            else:
                print("Please enter 1 or 2")
        except ValueError:
            print("Please enter a valid number")

def get_target_speed():
    """Get user input for target speed"""
    while True:
        try:
            speed = float(input("Enter target speed: "))
            return speed
        except ValueError:
            print("Please enter a valid number")

def get_motion_profile_options():
    """Get user selection for motion profile type"""
    print("\nMOTION PROFILE OPTIONS:")
    print("1. Hold current position (safe)")
    print("2. Move to zero position")
    print("3. Custom target positions")
    print("4. Smooth trajectory to target")
    
    while True:
        try:
            choice = int(input("Select motion profile (1-4): "))
            if 1 <= choice <= 4:
                return choice
            else:
                print("Please enter a number between 1 and 4")
        except ValueError:
            print("Please enter a valid number")

def get_custom_positions(num_motors):
    """Get custom target positions from user"""
    positions = []
    print(f"\nEnter target positions for {num_motors} motors (in radians):")
    for i in range(num_motors):
        while True:
            try:
                pos = float(input(f"Motor {i+1} target position: "))
                positions.append(pos)
                break
            except ValueError:
                print("Please enter a valid number")
    return positions

def get_trajectory_duration():
    """Get trajectory duration from user"""
    while True:
        try:
            duration = float(input("Enter trajectory duration (seconds): "))
            if duration > 0:
                return duration
            else:
                print("Duration must be positive")
        except ValueError:
            print("Please enter a valid number")

def get_safe_speed():
    """Get safe speed limit for position control"""
    while True:
        try:
            speed = float(input("Enter safe speed limit (deg/s, recommended 5-15): "))
            if 0 < speed <= 50:  # Reasonable safety limit
                return speed
            else:
                print("Speed must be between 0 and 50 deg/s")
        except ValueError:
            print("Please enter a valid number")

def get_snake_motion_parameters():
    """Get parameters for snake locomotion"""
    print("\nSNAKE MOTION PARAMETERS:")
    
    # Get speed
    while True:
        try:
            speed = float(input("Enter motion speed (0.01-0.5, recommended 0.1): "))
            if 0.01 <= speed <= 0.5:
                break
            else:
                print("Speed must be between 0.01 and 0.5")
        except ValueError:
            print("Please enter a valid number")
    
    # Get amplitude
    while True:
        try:
            amplitude = float(input("Enter motion amplitude in radians (0.1-1.0, recommended 0.3): "))
            if 0.1 <= amplitude <= 1.0:
                break
            else:
                print("Amplitude must be between 0.1 and 1.0 radians")
        except ValueError:
            print("Please enter a valid number")
    
    return speed, amplitude

def get_snake_motion_mode():
    """Get user selection for snake locomotion mode"""
    print("\nSNAKE LOCOMOTION MODES:")
    print("1. Serpentine motion (traditional snake movement)")
    print("2. Sidewinding motion (sidewinder rattlesnake style)")
    print("3. Concertina motion (accordion-like movement)")
    print("4. Slither motion (smooth undulating movement)")
    print("5. Back to main menu")
    
    while True:
        try:
            choice = int(input("Select snake motion mode (1-5): "))
            if 1 <= choice <= 5:
                return choice
            else:
                print("Please enter a number between 1 and 5")
        except ValueError:
            print("Please enter a valid number")

def main_menu():
    """Main interactive menu"""
    print("\n" + "="*60)
    print("ARCSNAKE INTERACTIVE TESTING SYSTEM")
    print("="*60)
    print("1. Print motor data")
    print("2. Run position control (U-joint motors)")
    print("3. Run speed control (Screw motors)")
    print("4. Run full system test (position + speed control)")
    print("5. Run enhanced motion profile control")
    print("6. Run snake locomotion modes")
    print("7. Print motor information")
    print("8. Stop and exit")
    
    while True:
        try:
            choice = int(input("\nSelect an option (1-8): "))
            if 1 <= choice <= 8:
                return choice
            else:
                print("Please enter a number between 1 and 8")
        except ValueError:
            print("Please enter a valid number")

if __name__ == "__main__":
    # Initialize CAN bus
    print("Initializing CAN bus...")
    core.CANHelper.init("can0")
    can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

    ### Screw shell motors (24V)
    screw_head_end = CanMotor(can0, motor_id = 3, gear_ratio = 5) # CHECK GEAR RATIO
    screw_head_mid = CanMotor(can0, motor_id = 4, gear_ratio = 5)
    screw_tail_mid = CanMotor(can0, motor_id = 1, gear_ratio = 5)
    screw_tail_end = CanMotor(can0, motor_id = 0, gear_ratio = 5)
    screw_motors = [screw_head_end, screw_head_mid, screw_tail_mid, screw_tail_end]

    ### U-joint motors (51V)
    # U-joints pointing head to tail, with segment location
    joint_h2t_head = CanMotor(can0, motor_id = 7, gear_ratio = 1) # CHECK GEAR RATIO
    joint_h2t_mid = CanMotor(can0, motor_id = 6, gear_ratio = 1)
    joint_h2t_tail = CanMotor(can0, motor_id = 5, gear_ratio = 1)

    # U-joints pointing tail to head, with segment location
    joint_t2h_head = CanMotor(can0, motor_id = 9, gear_ratio = 1)
    joint_t2h_mid = CanMotor(can0, motor_id = 10, gear_ratio = 1)
    joint_t2h_tail = CanMotor(can0, motor_id = 8, gear_ratio = 1)
    joint_motors = [joint_h2t_head, joint_h2t_mid, joint_h2t_tail,
                     joint_t2h_head, joint_t2h_mid, joint_t2h_tail]

    all_motors = screw_motors + joint_motors  # Combine all motors into one list
    
    # Predefined motor groups
    head_screw_motors = [screw_head_end, screw_head_mid]
    head_joint_motors = [joint_h2t_head, joint_t2h_head]
    head_all = head_screw_motors + head_joint_motors
    
    tail_screw_motors = [screw_tail_mid, screw_tail_end]
    tail_joint_motors = [joint_h2t_tail, joint_t2h_tail]
    tail_all = tail_screw_motors + tail_joint_motors
    
    # Individual motor mapping
    individual_motors = {
        1: screw_head_end, 2: screw_head_mid, 3: screw_tail_mid, 4: screw_tail_end,
        5: joint_h2t_head, 6: joint_h2t_mid, 7: joint_h2t_tail,
        8: joint_t2h_head, 9: joint_t2h_mid, 10: joint_t2h_tail
    }

    # --- BEGIN: Functionality matching test_sylvester, but with user selection ---
    try:
        # User selects which motors to use
        motor_choice = get_motor_selection()
        if motor_choice == 6:
            individual_choice = get_individual_motor()
            selected_screw_motors = [individual_motors[individual_choice]] if individual_motors[individual_choice] in screw_motors else []
            selected_joint_motors = [individual_motors[individual_choice]] if individual_motors[individual_choice] in joint_motors else []
        elif motor_choice == 1:
            selected_screw_motors = screw_motors
            selected_joint_motors = joint_motors
        elif motor_choice == 2:
            selected_screw_motors = screw_motors
            selected_joint_motors = []
        elif motor_choice == 3:
            selected_screw_motors = []
            selected_joint_motors = joint_motors
        elif motor_choice == 4:
            selected_screw_motors = head_screw_motors
            selected_joint_motors = head_joint_motors
        elif motor_choice == 5:
            selected_screw_motors = tail_screw_motors
            selected_joint_motors = tail_joint_motors
        else:
            selected_screw_motors = []
            selected_joint_motors = []

        selected_motors = selected_screw_motors + selected_joint_motors
        print(f"\nSelected {len(selected_motors)} motor(s) for testing")

        # Use the same CAN and init sequence as test_sylvester
        listener, notifier = init_listen_notify(can0, selected_motors)
        init_motors(selected_motors)
        start_send(selected_motors)

        # Always lock U-joint positions if any are present
        if selected_joint_motors:
            target_positions = set_motion_profile(selected_joint_motors)
            position_control(selected_joint_motors, target_positions)

        # User selects mode and speed for screw motors
        if selected_screw_motors:
            mode = get_speed_mode()
            speed = get_target_speed()
            speed_control(selected_screw_motors, speed, mode)
        else:
            print("No screw motors selected. Only U-joints will be locked in position.")

        # Print motor data in a loop, as in test_sylvester
        while True:
            print_motor_data(selected_motors)

        # --- END: Commenting out the rest of the interactive features for future reference ---
        '''
        # The following code is commented out to restrict functionality as requested.
        # Initialize motion controller for enhanced control
        # motion_controller = ARCSnakeMotionController(selected_motors)
        # Initialize snake locomotion controller
        # snake_controller = SnakeLocomotionController(selected_motors, num_segments=len(selected_motors))
        # Main interactive loop
        # while True:
        #     choice = main_menu()
        #     # ...existing code for menu options...
        '''

    except Exception as e:
        print("Error occurred:", e)
    except KeyboardInterrupt:
        print("\nKeyboard interrupt detected.")
    finally:
        stop_motors(can0, selected_motors)
