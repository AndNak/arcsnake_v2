import can
import math
from .CanUtils import CanUtils
from .timeout import timeout

class CanMotor(object):
    def __init__(self, bus, motor_id, gear_ratio, MIN_POS = -999 * 2 * math.pi, MAX_POS = 999 * 2 * math.pi):
        """Intializes motor with CAN communication 
        -

        Args:
            bus (can0 or can1): CAN port of motor??? check with florian
            motor_id (0x140 + ID (0-32)): Set motor_id
            gear_ratio (int): Set gear ratio between motor -> output. 
                Ex: RMD X8 Motor has a 6:1 gear ratio so this value would be 6
            MIN_POS (RAD, optional): Set MIN_POS of motor. Used in pos_ctrl function. Defaults to -999*2*math.pi.
            MAX_POS (RAD, optional): Set MAX_POS of motor. Used in pos_ctrl function. Defaults to 999*2*math.pi.
        """        
        self.canBus = bus
        self.utils = CanUtils()
        self.gear_ratio = gear_ratio
        self.id = motor_id
        self.min_pos = MIN_POS
        self.max_pos = MAX_POS

        # For some reason, the screw motor in one our debug sessions
        # required two of these to be sent in order to recieve new commands...
        self.send([0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        self.send([0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    

    '''
    Basic CANBus send command:
        - data is of the form: [0x{Register}, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00]
            - To convert a 32 unsigned integer to bytes for this, use toBytes in CanUtils
        - If wait_for_response is True, then this a "read" CANBus send. If False, then this is only a "send" command
            - To decode the return message, use readBytesList or readByte in CanUtils
    '''
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
        """Reads motor Torque, Speed, and Position from the motor.
        -

        Returns:
            (AMPs, RAD/S, RAD): Retrusn tuple of motor torque, speed, and position
        """
        msg = self.send([0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        # encoder readings are in (high byte, low byte)
        torque   = self.utils.readBytes(msg.data[3], msg.data[2])
        speed    = self.utils.readBytes(msg.data[5], msg.data[4]) / self.gear_ratio
        position = self.utils.readBytes(msg.data[7], msg.data[6]) / self.gear_ratio

        return (self.utils.encToAmp(torque), 
                self.utils.degToRad(speed), 
                self.utils.degToRad(self.utils.toDegrees(position)))


    def read_singleturn_position(self):
        """ Get single-turn position reading from encoder in radians. 
        -
        """
        (_, _, p) = self.read_motor_status()
        return p

    def read_raw_position(self):
        """Get raw position of encoder from -32768 to 32768 
        -
        """        
        msg = self.send([0x9c, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)
        position = self.utils.readBytes(msg.data[7], msg.data[6]) 
        return position


    def read_multiturn_position(self):
        ''' Get multi-turn position reading from encoder in radians
        -
        '''
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

    def read_speed(self):
        ''' Get speed reading from the encoder in rad/s
        -
        '''
        (_, s, _) = self.read_motor_status()
        return s
    

    def read_torque(self):
        ''' Get torque reading from the encoder in Amps
        -
        '''
        (t, _, _) = self.read_motor_status()
        return t

    def read_motor_pid(self):
        ''' Returns P and I values for pos, speed, and torque, can't get 'd' for some reason
        -

        Returns:
            (pos_p, pos_i, speed_p, speed_i, torque_p, torque_i): Returns tuple of P and I values
        '''
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

 
    def pos_ctrl(self, to_rad, max_speed = 999 * 2 * math.pi):
        """Set multiturn position control
        -

        Args:
            to_rad (RAD): Desired multi-turn angle in Radians
            max_speed (RAD/s, optional): Set max speed in rad/s. Defaults to 999*2*math.pi.
        """        
        if (to_rad < self.min_pos):
            to_rad = self.min_pos
        
        if (to_rad >= self.max_pos):
            to_rad = self.max_pos
        
        # The least significant bit represents 0.01 degrees per second.
        to_deg = 100 * self.utils.radToDeg(to_rad) * self.gear_ratio
        max_speed = self.utils.radToDeg(max_speed) * self.gear_ratio

        s_byte1, s_byte2 = self.utils.int_to_bytes(int(max_speed), 2)

        byte1, byte2, byte3, byte4 = self.utils.int_to_bytes(int(to_deg), 4)

        self.send([0xa4, 0x00, s_byte2, s_byte1, byte4, byte3, byte2, byte1])

    def pos_pid_ctrl(self, kp, ki):
        # read other values first
        msg = self.send([0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)

        speed_p  = msg.data[4]
        speed_i  = msg.data[5]
        torque_p = msg.data[6]
        torque_i = msg.data[7]

        self.send([0x32, 0x00, kp, ki, speed_p, speed_i, torque_p, torque_i])

    def speed_ctrl(self, to_rad, max_speed=20*2*math.pi):
        """Set speed in rad/s 
        -

        Args:
            to_rad (RAD): Set speed
            max_speed (RAD/s, optional): Set max allowable speed. Defaults to 20*2*math.pi.

        Returns:
            RAD/s: Returns current speed
        """        
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


    def setmultiTurnZeroOffset(self, offset, InvertDirection = None):
        byte1, byte2, byte3, byte4, byte5, byte6 = self.utils.int_to_bytes(offset, 6)

        if InvertDirection is None:
            self.send([0x63, byte6, byte5, byte4, byte3, byte2, byte1, 1], wait_for_response=True)
        else:
            self.send([0x63, byte6, byte5, byte4, byte3, byte2, byte1, 0], wait_for_response=True)
    

    def read_multiTurnZeroOffset(self):
        msg = self.send([0x22, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00], wait_for_response=True)
        
        # CANNOT USE msg.data directly because it is not iterable for some reason...
        # This is a hack to fix the bug
        byte_list = []
        for idx in range(1, 6):
            byte_list.append(msg.data[idx])
        byte_list.reverse()
        
        return self.utils.readBytesList(byte_list)

    
    def motor_stop(self):
        """Stops the motor. Useful for allowing motor to be turned by hand
        -
        """
        self.send([0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])