import os
import can
import math
import warnings
from .CanUtils import CanUtils
from .timeout import timeout

class CanMotor(object):
    def __init__(self, bus, gear_ratio, motor_id):
        self.canBus = bus
        self.utils = CanUtils()
        self.gear_ratio = gear_ratio
        self.id = motor_id

        # For some reason, the screw motor in one our debug sessions
        # required two of these to be sent in order to recieve new commands...
        self.send([0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.send([0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    
    @timeout(1)
    def send(self, data, wait_for_response = False):
        msg = can.Message(arbitration_id=self.id, data=data, is_extended_id=False)
        self.canBus.send(msg)

        if wait_for_response:
            while True:
                # Checking canbus message recieved with keyboard interrupt saftey
                try:
                    msg = self.canBus.recv()
                    if msg.arbitration_id == self.id:
                        break
                except (KeyboardInterrupt, ValueError) as e:
                    print(e)
                    break
            return msg
        else:
            return  None



    def read_motor_err_and_voltage(self):
        msg = self.send([0x9a, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        temp      = msg.data[1]
        voltage   = self.utils.readBytes(msg.data[4], msg.data[3]) / 10
        err_state = msg.data[7]

        return (temp, 
                voltage, 
                err_state)

    '''
    returns motor encoder readings in units of:
    torque current 
        bit range: -2048~2048 ==> real range: -33A~33A
    speed
        1 degree/s/LSB ==> 1 rad/s/LSB
    position
        14-bit range: 0~16383 deg ==> rad
    '''
    def read_motor_status(self):
        msg = self.send([0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        # encoder readings are in (high byte, low byte)
        torque   = self.utils.readBytes(msg.data[3], msg.data[2])
        speed    = self.utils.readBytes(msg.data[5], msg.data[4]) / self.gear_ratio
        position = self.utils.readBytes(msg.data[7], msg.data[6]) / self.gear_ratio

        return (self.utils.encToAmp(torque), 
                self.utils.degToRad(speed), 
                self.utils.degToRad(self.utils.toDegrees(position)))

    '''
    get just the position reading from the encoder
    '''
    def read_position(self):
        (_, _, p) = self.read_motor_status()
        return p

    '''
    get multi-turn position reading from encoder
    '''
    def read_multiturn_position(self):
        msg = self.send([0x92, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)
        
        # CANNOT USE msg.data directly because it is not iterable for some reason...
        # This is a hack to fix the bug
        byte_list = []
        for idx in range(1, 8):
            byte_list.append(msg.data[idx])
        byte_list.reverse()
        decimal_position = self.utils.readBytesList(byte_list)

        # Note: 0.01 scale is taken from dataset to convert multi-turn bits to degrees
        return self.utils.degToRad(0.01*decimal_position/self.gear_ratio)

    

    '''
    get just the speed reading from the encoder
    '''
    def read_speed(self):
        (_, s, _) = self.read_motor_status()
        return s
    
    '''
    get just the torque reading from the encoder
    '''
    def read_torque(self):
        (t, _, _) = self.read_motor_status()
        return t

    '''
    returns `p` and `i` values for position, speed, and torque. can't get `d` for some reason
    '''
    def read_motor_pid(self):
        msg = self.send([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        pos_p    = msg.data[2]
        pos_i    = msg.data[3]
        speed_p  = msg.data[4]
        speed_i  = msg.data[5]
        torque_p = msg.data[6]
        torque_i = msg.data[7]

        return (pos_p,    pos_i, 
                speed_p,  speed_i,
                torque_p, torque_i)

    '''
    sends the motor to position `to_rad` by converting from radians to degrees.
    `to_rad` must be a positive value.
    actual position sent is in units of 0.01 deg/LSB (36000 == 360 deg).
    rotation direction is determined by the difference between the target pos and the current pos
    '''
    def pos_ctrl(self, to_rad, min_pos=0, max_pos=2*math.pi):
        if (to_rad < min_pos):
            to_rad = min_pos
        
        if (to_rad >= max_pos):
            to_rad = max_pos
        
        # The least significant bit represents 0.01 degrees per second.
        to_deg = 100 * self.utils.radToDeg(to_rad) * self.gear_ratio
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_deg)

        self.send([0xa3, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1])

    def pos_pid_ctrl(self, kp, ki):
        # read other values first
        msg = self.send([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        speed_p  = msg.data[4]
        speed_i  = msg.data[5]
        torque_p = msg.data[6]
        torque_i = msg.data[7]

        self.send([0x32, 0x00, kp, ki, speed_p, speed_i, torque_p, torque_i])

    '''
    controls the speed of the motor by `to_deg` rad/s/LSB by converting from rad/s/LSB to dps/LSB.
    actual speed sent is in units of 0.01 dps/LSB.
    '''
    def speed_ctrl(self, to_rad, max_speed=20*math.pi):
        if to_rad > max_speed:
            to_rad = max_speed

        to_dps = self.gear_ratio * 100 * self.utils.radToDeg(to_rad)
        byte1, byte2, byte3, byte4 = self.utils.toBytes(to_dps)
 
        msg = self.send([0xa2, 0x00, 0x00, 0x00, byte4, byte3, byte2, byte1], wait_for_response=True)
        return self.utils.degToRad(self.utils.readBytes(msg.data[5], msg.data[4])) / self.gear_ratio

    def speed_pid_ctrl(self, kp, ki):
        msg = self.send([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        pos_p    = msg.data[2]
        pos_i    = msg.data[3]
        torque_p  = msg.data[6]
        torque_i  = msg.data[7]

        self.send([0x31, 0x00, pos_p, pos_i, kp, ki, torque_p, torque_i])

    '''
    controls the torque current output of the motor. 
    actual control value sent is in range -2000~2000, corresponding to -32A~32A
    '''
    def torque_ctrl(self, low_byte, high_byte):
        self.send([0xa1, 0x00, 0x00, 0x00, low_byte, high_byte, 0x00, 0x00])

    def torque_pid_ctrl(self, kp, ki):
        msg = self.send([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        pos_p    = msg.data[2]
        pos_i    = msg.data[3]
        speed_p  = msg.data[4]
        speed_i  = msg.data[5]

        self.send([0x31, 0x00, pos_p, pos_i, speed_p, speed_i, kp, ki])

    '''
    force-stops the motor.
    '''
    def motor_stop(self):
        self.send([0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])