from randomc.random import Rand48
import math
import os
import sys


def next_exp():
    return random.next()


# 1
def arrival():
    return math.floor(next_exp())


# 2
def bursts():
    # this doesnt work yet
    return math.ceil(random.srand(1) * 64)


# 3


if __name__ == "__main__":
    # error check arguments
    if len(sys.argv) != 6:
        print("Usage: python script.py n n_cpu seed lambda_arg e")
        sys.exit(1)

    _, n, n_cpu, seed, lambda_arg, e = sys.argv
    print(
        f"<<< PROJECT PART I -- process set (n={n}) with {n_cpu} CPU-bound process >>>"
    )
    # print(f"I/O-bound process {}: arrival time {}ms; {} CPU bursts:")
    # print(f"--> CPU burst {}ms --> I/O burst {}ms")

    # This is NOT the python library module.
    random = Rand48(0)

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
