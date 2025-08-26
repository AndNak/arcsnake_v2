from core.CanMotorNew import CanMotor
from core.MotorListener import MotorListener
import core.CANHelper
import can
import time
import numpy as np

### 0 (24V), 
### 1 (24V), 5 (51V)
### 4 (24V), 6 (51V)
### 3 (24V), 7 (51V)

if __name__ == "__main__":

	# Initialize CAN bus
	core.CANHelper.init("can0")
	can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

	# Initial CanMotor objects (does not try to send any messages yet)
	### Screw motors
	motor0 = CanMotor(can0, motor_id = 0, gear_ratio = 1)
	motor1 = CanMotor(can0, motor_id = 1, gear_ratio = 1)
	motor2 = CanMotor(can0, motor_id = 4, gear_ratio = 1)
	motor3 = CanMotor(can0, motor_id = 3, gear_ratio = 1)
	### U-Joints
	motor4 = CanMotor(can0, motor_id = 5, gear_ratio = 1)
	motor5 = CanMotor(can0, motor_id = 6, gear_ratio = 1)
	motor6 = CanMotor(can0, motor_id = 7, gear_ratio = 1)
	motor7 = CanMotor(can0, motor_id = 8, gear_ratio = 1)
	motor8 = CanMotor(can0, motor_id = 9, gear_ratio = 1)
	motor9 = CanMotor(can0, motor_id = 10, gear_ratio = 1)

	motor_list = [motor0, motor1, motor2, motor3, motor4, motor5, motor6, motor7, motor8, motor9]  # Add all motors to the listener
	print(len(motor_list), " motors in list")
	motor_listener = MotorListener(motor_list=motor_list)
	input("Start Notifier")

	# Start Notifier to listen for messages

	notifier = can.Notifier(can0, [motor_listener])

	# Start motor initialization after user input (this sends start command to motors, etc.)
	
	input("Initialize motors")
	for motor in motor_list:
		motor.initialize_motor()

	# Wait 1 s, then start periodic sends after user input
	time.sleep(1)
	
	input("Start periodic sends")

	for motor in motor_list:
		motor.read_status_periodic()
		motor.read_multiturn_periodic()
		motor.read_motor_state_periodic()
	"""
	motor1.read_status_periodic()
	motor1.read_multiturn_periodic()
	motor1.read_motor_state_periodic()
	"""
	# Start speed control while also reading and printing motor data
	command_speed = -20
	# command_speed = -5

	target_position = [1.3465, -1.0744, 2.0263, 0.4740, -1.5247, 2.7009]

	input("Start position control")
	for idx, motor in enumerate(motor_list):
		if idx >= 4:
			motor.initialize_control_command()
			motor.set_control_mode("position", target_position[idx - 4])
		else:
			pass

	input("Start speed control")
	# motor1.target_speed = command_speed
	# motor1.motor_data.command_mode = "speed"
	for idx, motor in enumerate(motor_list):
		if idx < 2:
			motor.initialize_control_command()
			motor.set_control_mode("speed", command_speed)
		elif idx < 4:
			motor.initialize_control_command()
			motor.set_control_mode("speed", -command_speed)
		else:
			pass
			

	# """
	# motor5.initialize_control_command()
	# motor5.set_control_mode("speed", command_speed)
	# motor0.initialize_control_command()
	# motor0.set_control_mode("speed", command_speed)
	
	# # motor1.motor_resume()
	# motor1.clear_error_flag()  # Clear any latched errors
	# motor1._single_send([0x88])  # Direct enable command
	

	#initial_pos = motor1.motor_data.multiturn_position
	#print("Initial position: ", initial_pos)

	

	try:
		while True:
			print(motor9.motor_data)
			time.sleep(0.1)
			pass

	except KeyboardInterrupt:
		#motor1.stop_all_tasks()
		for motor in motor_list:
			motor.stop_all_custom_periodic()
			motor.motor_off()
		# motor1.stop_all_custom_periodic()
		# motor1.motor_off()
		core.CANHelper.cleanup("can0")
		can0.shutdown()
		print("Exiting")
		exit(0)
