import os
import can
from CanMotor import CanMotor

class CanScrewMotor(CanMotor):
    def __init__(self):
        CanMotor.__init__(self)

    def read_encoder():
        msg = send(0x141, [0x90, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])
        # data = msg.data

        # print(msg)
        # print("cmd_byte = " + str(data[0]))
        # # current relative position 
        # print("new_pos = " + str(readBytes(data[3], data[2])))
        # # current original position
        # print("orig_pos = " + str(readBytes(data[5], data[4])))
        # # offset from original position
        # print("offset = " + str(readBytes(data[7], data[6])))

    # def motor_running():
    #     msg = send(0x141, [0x88, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    # def motor_stop():
    #     msg = send(0x141, [0x81, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00])

    # def pos_ctrl(low_byte, mid_byte1, mid_byte2, high_byte):
    #     msg = send(0x141, [0xa3, 0x00, 0x00, 0x00, low_byte, mid_byte1, mid_byte2, high_byte])
    #     data = msg.data

    #     print(msg)
    #     print("cmd_byte = " + str(data[0]))
    #     print("motor temp = " + str(data[1]))
    #     print("torque current = " + str(readBytes(data[3], data[2])))
    #     print("speed = " + str(readBytes(data[5], data[4])))
    #     print("encoder position = " + str(readBytes(data[7], data[6])))

    