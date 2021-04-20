import math

HEXBASE = 16
TWOBYTE_VAL = HEXBASE * HEXBASE

class CanUtils:
    # convert values from 2-byte hexadecimal to decimal
    def readBytes(self, high_byte, low_byte):
        decimal_val = high_byte*256 + low_byte

        if ((high_byte & 0x80) != 0):  # if MSB is 1
            decimal_val = -1*(((decimal_val) ^ 0xffff) + 1)  # 2's complement
        
        return decimal_val

    # convert value from decimal to 2-byte hexadecimal
    def toBytes(self, amt):
        amt = int(amt)

        if (amt < 0):
            amt = ((-amt) ^ 0xffff) + 1  # 2's complement

        byte1 = (amt & 0xf000) >> 12
        byte2 = (amt & 0xf00)  >> 8
        byte3 = (amt & 0xf0)   >> 4
        byte4 = (amt & 0xf)

        return byte1, byte2, byte3, byte4

    # convert 14-bit encoder (range 0~16383) current position to degrees 
    # seems like 360 degrees = 15800 encoder bit value
    def toDegrees(self, enc_position):
        return (enc_position*360/15800)
        # return enc_position

    # convert degrees to radians
    def degToRad(self, in_deg):
        return math.pi * in_deg / 180

    # convert radians to degrees
    def radToDeg(self, in_rad):
        return 180 * in_rad / math.pi

    # convert encoder bits to amps
    def encToAmp(self, in_enc):
        return in_enc * 33 / 2048

    # convert amps to encoder bits
    def ampToEnc(self, in_amp):
        return in_amp * 2000 / 32