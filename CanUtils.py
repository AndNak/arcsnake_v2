class CanUtils:
    def readBytes(self, high_byte, low_byte):
        return high_byte*256 + low_byte

    def writeBytes(self, amt):
        return int(amt // 256), int(amt % 256)

    def toDegrees(self, enc_position):
        return (359 * enc_position)/16383
        # return enc_position / 100