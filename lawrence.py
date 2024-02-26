import random
import math
import os
import sys

if len(sys.argv) != 6:
    print("Usage: python script.py a b c d e")
    sys.exit(1)

_, n, n_cpu, seed, lambda_arg, e = sys.argv
print(f"<<< PROJECT PART I -- process set (n={n}) with {n_cpu} CPU-bound process >>>")
# print(f"I/O-bound process {}: arrival time {}ms; {} CPU bursts:")
# print(f"--> CPU burst {}ms --> I/O burst {}ms")


class drand48:
    def __init__(self, seed=0):
        self.state = seed & 0xFFFFFFFFFFFF  # Ensure seed is 48-bit

    def rand(self):
        self.state = (0x5DEECE66D * self.state + 0xB) & 0xFFFFFFFFFFFF
        return self.state / 0x1000000000000  # Scale to [0, 1)


random_gen = drand48(seed=12345)


def next_exp():
    return 30.5


def arrival():
    return math.floor(next_exp())


def bursts():
    return math.ceil(random_gen.rand() * 64)


print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
print(bursts())
