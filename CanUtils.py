import math

HEXBASE = 16
TWOBYTE_VAL = HEXBASE * HEXBASE

class CanUtils:
    # convert values from 2-byte hexadecimal to decimal
    def readBytes(self, high_byte, low_byte):
        return high_byte*256 + low_byte

    # convert value from decimal to 2-byte hexadecimal
    def toBytes(self, amt):
        byte1 = int(amt // (TWOBYTE_VAL ** 3))
        amt = amt % (TWOBYTE_VAL ** 3)
        byte2 = int(amt // (TWOBYTE_VAL ** 2))
        amt = amt % (TWOBYTE_VAL ** 2)
        byte3 = int(amt // TWOBYTE_VAL)
        byte4 = int(amt % TWOBYTE_VAL)
        return byte1, byte2, byte3, byte4

    # convert 14-bit encoder (range 0~16383) current position to degrees 
    # seems like 360 degrees = 15800 encoder bit value
    def toDegrees(self, enc_position):
        return (enc_position*360/15800)
        # return enc_position

    # convert degrees to radians
    def toRadians(self, in_deg):
        return math.pi * in_deg / 180