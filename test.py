import os
import can

def init():
    os.system('sudo ifconfig can0 down')
    os.system('sudo ip link set can0 type can bitrate 1000000')
    os.system('sudo ifconfig can0 up')

def readBytes(high_byte, low_byte):
    return high_byte*256 + low_byte

def send(arb_id, data):
    can0 = can.interface.Bus(channel='can0', bustype='socketcan_ctypes')

    msg = can.Message(arbitration_id=arb_id, data=data, extended_id=False)
    can0.send(msg)
    msg = can0.recv()
    return msg

def read_encoder():
    msg = send(0x141, [0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    data = msg.data

    print(msg)
    print("cmd_byte = " + str(data[0]))
    print("new_pos = " + str(readBytes(data[3], data[2])))
    print("orig_pos = " + str(readBytes(data[5], data[4])))
    print("offset = " + str(readBytes(data[7], data[6])))

def motor_running():
    msg = send(0x141, [0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

def motor_stop():
    msg = send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

def read_PID():
    msg = send(0x141, [0x30, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
    data = msg.data

    print(msg)
    print("cmd_byte = " + str(data[0]))
    print("pos_kp = " + str(data[2]))
    print("pos_ki = " + str(data[3]))
    print("speed_kp = " + str(data[4]))
    print("speed_ki = " + str(data[5]))
    print("torque_kp = " + str(data[6]))
    print("torque_ki = " + str(data[7]))

def write_PID(pos_kp, pos_ki, speed_kp, speed_ki, torque_kp, torque_ki):
    msg = send(0x141, [0x31, 0x00, pos_kp, pos_ki, speed_kp, speed_ki, torque_kp, torque_ki])
    data = msg.data

    print(msg)
    print("cmd_byte = " + str(data[0]))
    print("pos_kp = " + str(data[2]))
    print("pos_ki = " + str(data[3]))
    print("speed_kp = " + str(data[4]))
    print("speed_ki = " + str(data[5]))
    print("torque_kp = " + str(data[6]))
    print("torque_ki = " + str(data[7]))

def pos_ctrl(low_byte, mid_byte1, mid_byte2, high_byte):
    msg = send(0x141, [0xa3, 0x00, 0x00, 0x00, low_byte, mid_byte1, mid_byte2, high_byte])
    data = msg.data

    print(msg)
    print("cmd_byte = " + str(data[0]))
    print("motor temp = " + str(data[1]))
    print("torque current = " + str(readBytes(data[3], data[2])))
    print("speed = " + str(readBytes(data[5], data[4])))
    print("encoder position = " + str(readBytes(data[7], data[6])))

def cleanup():
    os.system('sudo ifconfig can0 down')

if __name__ == '__main__':
    init()

    data0 = 0xa3
    data1 = 0x00
    data2 = 0x00
    data3 = 0x00
    data4 = 0x10
    data5 = 0x00
    data6 = 0x00
    data7 = 0x00
    data = [data0, data1, data2, data3, data4, data5, data6, data7]
    # send(0x141, data)
    # write_PID(0x80, 0x00, 0x20, 0x00, 0x20, 0x00)
    read_encoder()
    # read_PID()
    # motor_stop()
    # motor_running()

    # cleanup()