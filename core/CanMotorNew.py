import can
import math
from .CanUtils import CanUtils
from .timeout import timeout
import time
from core.timeout import TimeoutError
import pandas as pd
from dataclasses import dataclass
from typing import Tuple
from can import ThreadSafeBus

# Dataclass for storing current motor data, will be updated on receiving new messages
@dataclass
class MotorData:
	singleturn_position: float = 0
	multiturn_position: float = 0
	target_position: float = 0
	speed: float = 0
	target_speed: float = 0
	acceleration: float = 0
	torque: float = 0
	temperature: float = 0
	voltage: float = 0
	error_state: str = ""
	PI_values: Tuple[int, int, int, int, int, int] = (0, 0, 0, 0, 0, 0) # Kp_pos, Ki_pos, Kp_speed, Ki_speed, Kp_torque, Ki_torque
	last_update: Tuple[int, float] = (0, 0) # (msg_type, timestamp). Could change this so each parameter has its own last update time
	command_mode: str = "" # This can be position, speed, (in theory torque one day)
	# Should we use timestamp from CAN message our our own timing, i.e. time.time() - self.wakeup_time?
	
# Class used for motor control, each instance represents a motor
class CanMotor(object):
	def __init__(self, bus:ThreadSafeBus, motor_id, gear_ratio, MIN_POS = -999 * 2 * math.pi, MAX_POS = 999 * 2 * math.pi, motor_type = "screw",
			  MAX_SPEED:float = (1890*2*math.pi)/60):
		"""Intializes motor object 
		-
		Args:
			bus (can0 or can1): CAN Bus that the motor is connected to
			motor_id (int) Set motor_id from 0-15. Can be determined by decimal number of the dip switches 
				Ex: If the dip switches are set to 0000, the motor_id would be 0. Since 0000 in binary to decimal is 0. 
			gear_ratio (int): Set gear ratio between motor -> output. 
				Ex: RMD X8 Motor has a 6:1 planteary gear ratio so this value would be 6
			MIN_POS (RAD, optional): Set MIN_POS of motor. Used in pos_ctrl function. Defaults to -999*2*math.pi.
			MAX_POS (RAD, optional): Set MAX_POS of motor. Used in pos_ctrl function. Defaults to 999*2*math.pi.
			MAX_SPEED (RAD/s, optional): Set MAX_SPEED of motor. Used in speed_ctrl function. Defaults to (1890*2*math.pi)/60.
		""" 

		# Set motor parameters   
		self.canBus = bus
		self.utils = CanUtils()
		self.gear_ratio = gear_ratio
		self.message_log = []
		self.wakeup_time = time.time()
		self.id = int(321 + motor_id) # arbitration id
		self.min_pos = MIN_POS
		self.max_pos = MAX_POS
		self.max_speed = MAX_SPEED

		# Encoder value range depends on motor type
		if motor_type == "joint":
			self.enc_value_range = 2*32767
		elif motor_type == "screw":
			self.enc_value_range = 16383

		# For storing current motor values, will be updated on receiving new messages
		self.motor_data = MotorData()

		# Store active tasks for stopping later
		self.active_tasks = []
		self.motor_control_task = None

	# Initialize motor for operation
	def initialize_motor(self):
		'''
		Prepare motor for operation by clearing any errors, testing communication, and setting initial values
		Ideally what we do here is check motor status, wait for the reply, check the status is good, clear any errors, and start motor
		TODO: Add a check to ensure motor actually receives these commands because we will only send one?
		'''
		# Clear motor errors and print for debug
		self.read_status_once()
		self.clear_error_flag()
		self.motor_off()
	
	# Called everytime a new message for this motor is recieved, filters according to msg type (first byte)
	def process_message(self, msg):
		'''
		Processes a message received by the Listener that matches this motor's ID
		'''

		# print("Processing message ", msg)
		
		# Exit early if it is a transmitted message
		if not msg.is_rx:
			return

		# Print if error flag is set to true on canbus message
		if msg.error_state_indicator:
			print("Error state indicator is set: ")
			print(msg)

		# filter based on message type
		# print("Received message ", hex(msg.data[0]))
		if msg.data[0] == 0x9a: # Read error and voltage
			#TODO: Err state should also use data[6]. Please add this in and look at the error codes
			temp = msg.data[1]
			voltage = self.utils.readBytesList([msg.data[4], msg.data[3]]) / 10
			# voltage_HB = msg.data[4]
			# voltage_LB = msg.data[3]
			err_state = msg.data[7]

			# find err_state as string according to status table in doc
			volt_bit = 1                              # bit 0
			temp_bit = 8                              # bit 3
			err_state_str = ["No errors"]             # string to return
			# check voltage status bit
			if err_state & volt_bit:
				err_state_str[0] = ""
				err_state_str.append("Low voltage protection flagged")
			# check temperature status bit
			if err_state & temp_bit:
				err_state_str[0] = ""
				err_state_str.append("Over temperature protection flagged")

			if err_state_str[0] == "": err_state_str.pop(0)
			err_state_str = ", ".join(err_state_str)

			self.motor_data.temperature = temp
			self.motor_data.voltage = voltage
			self.motor_data.error_state = err_state_str
			self.motor_data.last_update = (0x9a, msg.timestamp) 

			# print("Motor voltage = ", voltage, ", temperature = ", temp, ", Error State = ", err_state_str)
			
		elif msg.data[0] == 0x9c: # Read motor status (singleturn position, speed, torque)
			# encoder readings are in (high byte, low byte)
			torque = self.utils.readBytes(msg.data[3], msg.data[2])
			torque = self.utils.encToAmp(torque)
			speed = self.utils.readBytes(msg.data[5], msg.data[4]) / self.gear_ratio
			speed = self.utils.degToRad(speed)
			position = self.utils.readBytes(msg.data[7], msg.data[6]) / self.gear_ratio
			position = self.utils.degToRad(self.utils.toDegrees(position, self.enc_value_range))

			self.motor_data.singleturn_position = position
			self.motor_data.speed = speed
			self.motor_data.torque = torque
			self.motor_data.last_update = (hex(0x9c), msg.timestamp)

			# print("Singleturn position = ", position, ", speed = ", speed, ", torque = ", torque)

		elif msg.data[0] == 0x92: # Read multi-turn position
			byte_list = []
			for idx in range(1, 8):
				byte_list.append(msg.data[idx])
			byte_list.reverse()
			decimal_position = self.utils.readBytesList(byte_list)
			# Note: 0.01 scale is taken from dataset to convert multi-turn bits to degrees
			multiturn_position = self.utils.degToRad(0.01*decimal_position/self.gear_ratio)

			self.motor_data.multiturn_position = multiturn_position
			self.motor_data.last_update = (0x92, msg.timestamp)

		elif msg.data[0] == 0xa2 or msg.data[0] == 0xa4: # Reply to speed or position control command (equivalent message types)
			# TODO: add reading for other values/bytes in the message
			cur_speed = self.utils.degToRad(self.utils.readBytesList([msg.data[5], msg.data[4]])) / self.gear_ratio
			self.motor_data.speed = cur_speed
			self.motor_data.last_update = (0xa2, msg.timestamp)

		elif msg.data[0] == 0xa4: # Reply to position control command
			cur_pos = self.utils.degToRad(self.utils.readBytesList([msg.data[7], msg.data[6]])) / self.gear_ratio
			cur_speed = self.utils.degToRad(self.utils.readBytesList([msg.data[5], msg.data[4]])) / self.gear_ratio
			cur_torque = self.utils.encToAmp(self.utils.readBytes(msg.data[3], msg.data[2]))
			cur_temp = msg.data[1]
			self.motor_data.singleturn_position = cur_pos
			self.motor_data.speed = cur_speed
			self.motor_data.torque = cur_torque
			self.motor_data.temperature = cur_temp
			self.motor_data.last_update = (0xa4, msg.timestamp)

		else:
			# print("Unknown message type received, ", hex(msg.data[0]))
			pass

	# util function for sending periodic messages
	def _periodic_send(self, data, period, duration, modifier_callback = None):
		'''
		Default is every 10 ms indefinitely

		Args:
			data (byte list): data to send
			period (float): period in between each message (seconds)
			duration (float, optional): duration to send messages for (seconds). Defaults to None (meaning indefinitely
			modifier_callback (Callable[msg], optional): optional modifier callback fucntion.

		Returns:
			task object that can be used to stop periodic send
		'''
		# print("Starting periodic send of message ", hex(data[0]))
		msg = can.Message(arbitration_id=self.id, data=data, is_extended_id=False, is_rx=False)
		task = self.canBus.send_periodic(msg, period, duration, True, modifier_callback)
		self.active_tasks.append(task)
		return task

	# Stop all active tasks, empty active_tasks list
	def stop_all_tasks(self):
		for task in self.active_tasks:
			task.stop()
		self.active_tasks.clear()

	# util function for sending a single message, don't wait for reply
	def _single_send(self, data):
		'''
		utility function for sending a single message, don't wait for reply

		Args:
			data (byte list): data to send
		'''
		msg = can.Message(arbitration_id=self.id, data=data, is_extended_id=False, is_rx=False)
		self.canBus.send(msg)

	### Single send commands
	def clear_error_flag(self):
		'''
		Clears any error flags on the motor
		'''
		msg_data = [0x9B, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self._single_send(msg_data)

	def read_status_once(self):
		'''
		Reads the temperature, voltage, and error state of the motor
		'''
		msg_data = [0x9A, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self._single_send(msg_data)

	def motor_stop(self):
		'''
		Stops the motor, but does not clear operating state or previously received commands.
		'''
		# Set motor command to empty
		self.motor_data.command_mode = ""
		self.motor_data.target_speed = 0
		self.motor_data.target_position = 0

		msg_data = [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self._single_send(msg_data)
	
	def motor_resume(self):
		'''
		Resume motor operation (recover from motor stop command).
		'''
		msg_data = [0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self._single_send(msg_data)

	def motor_off(self):
		'''
		Turns off the motor, clearing operating state and previously received commands.
		'''
		# Set motor command to empty
		self.motor_data.command_mode = ""
		self.motor_data.target_speed = 0
		self.motor_data.target_position = 0
		
		msg_data = [0x80, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		self._single_send(msg_data)

	def read_status_periodic(self, period=0.1, duration=None):
		'''
		Periodic send for reading motor status (temp, voltage, error flag)
		Args:
			period (float): period in between each message (seconds)
			duration (float, optional): duration to send messages for (seconds). Defaults to None (meaning indefinitely)

		Returns:
			task object that can be used to stop periodic send
		'''
		msg_data = [0x9a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		task = self._periodic_send(msg_data, period, duration)
		return task

	def read_multiturn_periodic(self, period=0.1, duration=None):
		'''
		Periodic send for reading motor multiturn
		Args:
			period (float): period in between each message (seconds)
			duration (float, optional): duration to send messages for (seconds). Defaults to None (meaning indefinitely)

		Returns:
			task object that can be used to stop periodic send
		'''
		msg_data = [0x92, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		task = self._periodic_send(msg_data, period, duration)
		return task

	def read_motor_state_periodic(self, period=0.1, duration=None):
		'''
		Periodic send for reading motor state (single turn position, speed, and torque)
		Args:
			period (float): period in between each message (seconds)
			duration (float, optional): duration to send messages for (seconds). Defaults to None (meaning indefinitely)

		Returns:
			task object that can be used to stop periodic send
		'''
		msg_data = [0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
		task = self._periodic_send(msg_data, period, duration)
		return task

	def _motor_command_modifier_callback(self, msg):
		'''
		Modifier callback for speed control command.
		This should be added to the periodic send task as a modifier callback
		for sending speed control or position control commands.

		Will read from the motor_data object to determine the command mode and
		adjust the data being sent accordingly.

		Args:
			msg (can.Message): message to be modified
		'''

		# Case statement for different command modes
		if self.motor_data.command_mode == "speed":
			# Set the data to the speed control command
			target_speed = self.motor_data.target_speed

			# Clip target speed to max speed
			if target_speed > self.max_speed:
				target_speed = self.max_speed
			if target_speed < -self.max_speed:
				target_speed = -self.max_speed

			# Convert target speed to degrees per second and multiply by gear ratio and 100 (for some reason)
			target_speed = self.utils.radToDeg(target_speed) * self.gear_ratio * 100
			
			# Convert to bytes
			byte1, byte2, byte3, byte4 = self.utils.int_to_bytes(int(target_speed), 4)

			# Set the data to the speed control command
			msg.data = [0xa2, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1]
		
		elif self.motor_data.command_mode == "position":
			# Set the data to the position control command
			target_position = self.motor_data.target_position

			# Clip target position to min and max
			if target_position > self.max_pos:
				target_position = self.max_pos
			if target_position < self.min_pos:
				target_position = self.min_pos

			# Convert target position to degrees (and multiply by gear ratio and 100 for some reason)
			to_deg = 100 * self.utils.radToDeg(target_position) * self.gear_ratio

			# limit speed, choosing safe value of 10 deg/s
			max_speed =  10 * self.gear_ratio

			# Convert to bytes
			s_byte1, s_byte2 = self.utils.int_to_bytes(int(max_speed), 2)
			byte1, byte2, byte3, byte4 = self.utils.int_to_bytes(int(to_deg), 4)

			msg.data = [0xa4, 0x00, s_byte2, s_byte1, byte4, byte3, byte2, byte1]
		
		elif self.motor_data.command_mode == "torque":
			# Set the data to the torque control command
			target_torque = self.motor_data.target_torque

			# Clip target torque to max and min
			if target_torque > 32:
				target_torque = 32
			if target_torque < -32:
				target_torque = -32

			target_torque *= 2000 / 32  # Value range is -2000 to 2000
			byte1, byte2 = self.utils.int_to_bytes(int(target_torque), 2)

			# Set the data to the torque control command
			msg.data = [0xA1, 0x00, 0x00, 0x00, byte2, byte1, 0x00, 0x00]
		
		elif self.motor_data.command_mode == "":
			pass

		else:
			print("Unknown command mode")
			pass

		return msg
		

	def initialize_control_command(self,  period=0.1, duration=None):
		'''
		Initializes a periodic send task for sending control commands to the motor

		Args:
			period (float): period in between each message (seconds)
			duration (float, optional): duration to send messages for (seconds). Defaults to None (meaning indefinitely)
		'''

		if self.motor_control_task is not None:
			raise ValueError("Motor control task already initialized. Please stop it first")

		empty_data = [0, 0, 0, 0, 0, 0, 0, 0]
		self.motor_control_task = self._periodic_send(empty_data, period, duration, modifier_callback = self._motor_command_modifier_callback)


	def set_control_mode(self, mode, target_value):
		'''
			Sets the various control modes for the motor

			Args:
				mode (str): "speed" or "position" (in future torque)
				target_value (float): target value for the mode (i.e. radians for position and rad/s for speed)
		'''

		if self.motor_control_task is None:
			raise ValueError("Motor control task not initialized. Please call initialize_control_command() first")

		# Set target value in motor_data
		if mode == "speed":
			self.motor_data.command_mode = "speed"
			self.motor_data.target_speed = target_value
		elif mode == "position":
			self.motor_data.command_mode = "position"
			self.motor_data.target_position = target_value
		elif mode == "torque":
			self.motor_data.command_mode = "torque"
			self.motor_data.target_torque = target_value
		else:
			print("Unknown control mode")
			return