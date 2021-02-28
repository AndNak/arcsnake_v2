class CanUtils:
    # convert values from 2-byte hexadecimal to decimal
    def readBytes(self, high_byte, low_byte):
        return high_byte*256 + low_byte

    # convert value from decimal to 2-byte hexadecimal
    def writeBytes(self, amt):
        return int(amt // 256), int(amt % 256)

    # convert 14-bit encoder (range 0~16383) current position to degrees 
    # seems like 360 degrees = 15800 encoder bit value
    def toDegrees(self, enc_position):
        return (enc_position*360/15800)
        # return enc_position