HEXBASE = 16
TWOBYTE_VAL = HEXBASE * HEXBASE
amt = -5

if (amt < 0):
    amt = ((-amt) ^ 0xffff) + 1  # 2's complement

byte1 = (amt & 0xf000) >> 12
byte2 = (amt & 0xf00)  >> 8
byte3 = (amt & 0xf0)   >> 4
byte4 = (amt & 0xf)

print("%s %s %s %s" % (hex(byte1), hex(byte2), hex(byte3), hex(byte4)))