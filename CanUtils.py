import math
import numpy as np

class CanUtils:
    # convert values from 2-byte hexadecimal to decimal
    def readBytes(self, high_byte, low_byte):
        decimal_val = np.int16(np.uint16((high_byte << 8) | low_byte))
        return decimal_val

    # convert value from decimal to 4-byte hexadecimal
    def toBytes(self, amt):
        amt = np.uint32(np.int32(amt))

        byte1 = np.uint8((amt & 0xff000000) >> 24)
        byte2 = np.uint8((amt & 0xff0000) >> 16)
        byte3 = np.uint8((amt & 0xff00) >> 8)
        byte4 = np.uint8((amt & 0xff))

        return byte1, byte2, byte3, byte4

    # convert 14-bit encoder (range 0~16383) current position to degrees 
    # seems like 360 degrees = 15800 encoder bit value
    def toDegrees(self, enc_position):
        return (enc_position*360/16383)

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