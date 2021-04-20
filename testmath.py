import numpy as np

# convert values from 2-byte hexadecimal to decimal
def readBytes(high_byte, low_byte):
    decimal_val = np.int16(np.uint16((high_byte << 8) | low_byte))
    return decimal_val

# convert value from decimal to 4-byte hexadecimal
def toBytes(amt):
    amt = np.uint32(np.int32(amt))

    byte1 = np.uint8((amt & 0xff000000) >> 24)
    byte2 = np.uint8((amt & 0xff0000) >> 16)
    byte3 = np.uint8((amt & 0xff00) >> 8)
    byte4 = np.uint8((amt & 0xff))

    return byte1, byte2, byte3, byte4

byte1, byte2, byte3, byte4 = toBytes(-5)
print("%s %s %s %s" % (hex(byte1), hex(byte2), hex(byte3), hex(byte4)))

decimal_val = readBytes(byte3, byte4)
print(str(decimal_val))