from randomc.random import Rand48
import math
import os
import sys

if len(sys.argv) != 6:
    print("Usage: python script.py n n_cpu seed lambda_arg e")
    sys.exit(1)

_, n, n_cpu, seed, lambda_arg, e = sys.argv
print(f"<<< PROJECT PART I -- process set (n={n}) with {n_cpu} CPU-bound process >>>")
# print(f"I/O-bound process {}: arrival time {}ms; {} CPU bursts:")
# print(f"--> CPU burst {}ms --> I/O burst {}ms")

random_gen = Rand48(0)


def next_exp():
    return 30.5


def arrival():
    return math.floor(next_exp())


def bursts():
    return math.ceil(random_gen.next() * 64)


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
