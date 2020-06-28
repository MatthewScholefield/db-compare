import os
import random
from collections import namedtuple


def rand_string(size):
    return os.urandom(size).translate(tbl).decode()


def rand_dist_string(max_len, min_len=12, power=2):
    return rand_string(int(min_len + (max_len - min_len) * random.random() ** power + 0.5))


User = namedtuple('User', 'name email passwordHash about')
tbl = bytes.maketrans(bytearray(range(256)),
                      bytearray([ord(b'a') + b % 26 for b in range(256)]))