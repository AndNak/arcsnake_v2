import math
import numpy as np

class CanUtils:
    def readBytes(self, high_byte, low_byte):
        """Converts values from 2-byte hexadecimal to decimal value
        -
        """        
        decimal_val = np.int16(np.uint16((high_byte << 8) | low_byte))
        return decimal_val

    def readBytesList(self, byte_list):
        """Reads an array of bytes and returns an integer value
        -
        """        
        out = np.uint64(0)
        for byte in byte_list:
            # HACK: Numpy decided it does not want to bitshift when it is "unsafe" (aka overflow)
            # So using product and addition equivalent stuff instead
            # out = np.uint64((out << 8) | byte)
            out = (out * 2**8) + np.uint64(byte)

        # manually handling 2s compliment... This sucks
        if out > 2**(8*len(byte_list) - 1) - 1:
            out = -np.int64(2**(8*len(byte_list)) - out) - 1
        else:
            out = np.int64(out)
        return out

    def int_to_bytes(self, value, length):
        """Converts integer value to x-byte hexadecimal
        -
        Args:
            value (int): Input value
            length (int): Number of bytes you want to convert the input value to 

        Returns:
            Array of bytes
            Ex: 
                byte1, byte2, byte3, byte4
                Where byte1 = High byte 
                and   byte4 = Low byte

        """        
        result = []
        for i in range(0, length):
            result.append(np.uint8(value >> (i * 8) & 0xff))
        result.reverse()
        return result

    def toDegrees(self, enc_position):
        """Convert 14-bit encoder reading (range 0~32766) to degrees

        Args:
            enc_position (_type_): _description_

        Returns:
            _type_: _description_
        """
        return (enc_position*360/32766)

    def degToRad(self, in_deg):
        """Converts degrees to radians
        -
        """
        return math.pi * in_deg / 180

    def radToDeg(self, in_rad):
        """Converts radians to degrees
        -
        """        
        return 180 * in_rad / math.pi

    def encToAmp(self, in_enc):
        """Convert encoder bits to amps
        -
        """        
        return in_enc * 33 / 2048

    def ampToEnc(self, in_amp):
        """ Converts amps to encoder bits
        -
        """
        return in_amp * 2000 / 32


    # # convert value from decimal to 4-byte hexadecimal
    # def toBytes(self, amt):

    #     amt = np.uint32(np.int32(amt))

    #     byte1 = np.uint8((amt & 0xff000000) >> 24)
    #     byte2 = np.uint8((amt & 0xff0000) >> 16)
    #     byte3 = np.uint8((amt & 0xff00) >> 8)
    #     byte4 = np.uint8((amt & 0xff))

    #     return byte1, byte2, byte3, byte4
