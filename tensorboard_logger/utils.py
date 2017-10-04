from crccheck.crc import Crc32c


def apply_and(x):
    return x & 0xffffffff


def encode(data):
    data = Crc32c.calc(data)
    temp = apply_and(data)
    return apply_and(((temp >> 15) | apply_and(temp << 17)) + 0xa282ead8)
