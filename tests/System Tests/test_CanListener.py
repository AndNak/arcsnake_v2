from core.CanMotorNew import CanMotor
from core.MotorListener import MotorListener
import core.CANHelper
import can
import time

if __name__ == "__main__":

	# Initialize CAN bus
	core.CANHelper.init("can0")
	can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

	# Initial CanMotor objects (does not try to send any messages yet)
	motor_id = 0
	gear_ratio = 1
	motor1 = CanMotor("can0", motor_id, gear_ratio)
	
	# Initialize motor listener with list of motor objects
	motor_list = [motor1]
	motor_listener = MotorListener(motor_list=motor_list)

	# Initialize motors (this sends start command to motors, etc.)
	for motor in motor_list:
		motor.initialize_motor()

	# Start Notifier to listen for messages
	can.Notifier(can0, [motor_listener])

	# Start speed control while also reading and printing motor data
	command_speed = 10
	speed_ctrl_task = motor1.speed_ctrl_periodic(command_speed)
	read_status_task = motor1.read_status_periodic()
	try:
		while True:
			print(motor1.motor_data)
			time.sleep(0.1)
	except KeyboardInterrupt:
		speed_ctrl_task.stop()
		read_status_task.stop()
		core.CANHelper.cleanup("can0")
		can0.shutdown()
		print("Exiting")
		exit(0)


