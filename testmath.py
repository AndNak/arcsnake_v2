HEXBASE = 16
TWOBYTE_VAL = HEXBASE * HEXBASE
amt = -5

if (amt < 0):
    amt = ((-amt) ^ 0xffff) + 1  # 2's complement

byte1 = int(amt // (TWOBYTE_VAL ** 3))
amt = amt % (TWOBYTE_VAL ** 3)
byte2 = int(amt // (TWOBYTE_VAL ** 2))
amt = amt % (TWOBYTE_VAL ** 2)
byte3 = int(amt // TWOBYTE_VAL)
byte4 = int(amt % TWOBYTE_VAL)

print("%s %s %s %s" % (hex(byte1), hex(byte2), hex(byte3), hex(byte4)))