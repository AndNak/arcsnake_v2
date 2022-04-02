import os
import can

from os.path import dirname, realpath  
import sys  
arcsnake_v2_path = dirname(dirname(realpath(__file__)))  
sys.path.append(arcsnake_v2_path)  

import core.CANHelper
from core.CanUJoint import CanUJoint
from core.CanJointMotor import CanJointMotor
from core.CanScrewMotor import CanScrewMotor
import time

if __name__ == "__main__":
	core.CANHelper.init("can0")
	can0 = can.ThreadSafeBus(channel='can0', bustype='socketcan')

	joint1 = CanUJoint(can0, 0x141)

	# joint1.zero_motor()

	print(joint1.read_multiTurnZeroOffset())

	'''
	try:
		for i in range(1000):
			print(f"readpos: {joint1.read_raw_position()}  |  multiturn: {joint1.read_multiturn_position()}")
			time.sleep(0.1)
	except(KeyboardInterrupt) as e:
		print(e)
	
	joint1.pos_ctrl(0 * 2 * 3.1415)
	
	time.sleep(1)

	print(f"new readpos: {joint1.read_raw_position()}  |  multiturn: {joint1.read_multiturn_position()}")
	
	'''

	print('Done')
	
	
	joint1.motor_stop() # Disable the motor from moving

	core.CANHelper.cleanup("can0")