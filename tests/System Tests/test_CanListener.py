from core.CanMotorNew import CanMotor
from core.MotorListener import MotorListener
import core.CANHelper
import can
import time
from core.CanArduinoSensors import CanArduinoSensors

if __name__ == "__main__":

	# Initialize CAN bus
	core.CANHelper.init("can0")
	can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')


	# Initial CanMotor objects (does not try to send any messages yet)
	motor_id = 2
	gear_ratio = 1
	motor1 = CanMotor(can0, motor_id, gear_ratio)
	
	# Initialize motor listener with list of motor objects
	motor_list = [motor1]
	motor_listener = MotorListener(motor_list=motor_list)

	input("Continue")
	# Initialize motors (this sends start command to motors, etc.)
	for motor in motor_list:
		motor.initialize_motor()

	# Start Notifier to listen for messages
	can.Notifier(can0, [motor_listener])

	# Start speed control while also reading and printing motor data
	command_speed = 10
	motor1.read_status_periodic()
	motor1.read_multiturn_periodic(0.15)
	motor1.read_motor_state_periodic()

	motor1.initialize_control_command()
	# motor1.set_control_mode("speed", command_speed)
	motor1.set_control_mode("position", 3.14/2.0)

	try:
		while True:
			print(motor1.motor_data)
			time.sleep(1)
	except KeyboardInterrupt:
		motor1.stop_all_tasks()
		motor1.motor_off()
		core.CANHelper.cleanup("can0")
		can0.shutdown()
		print("Exiting")
		exit(0)


