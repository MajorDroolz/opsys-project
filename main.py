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
def generate_process(n):
    processes = []
    for _ in range(n):
        process = {}
        process["arrival_time"] = arrival()
        process["cpu_bursts"] = bursts()
        process["bursts"] = []
        for i in range(process["cpu_bursts"]):
            cpu_burst_time = math.ceil(next_exp())
            io_burst_time = math.ceil(next_exp()) * 10
            if i >= n - 26:
                cpu_burst_time *= 4
                io_burst_time = math.ceil(io_burst_time / 8)
                if i == process["cpu_bursts"] - 1:
                    process["bursts"].append((cpu_burst_time, None))
                else:
                    process["bursts"].append((cpu_burst_time, io_burst_time))
        processes.append(process)
    return processes


if __name__ == "__main__":
    # error check arguments
    if len(sys.argv) != 6:
        print("Usage: python script.py n n_cpu seed lambda_arg threshold")
        sys.exit(1)

    _, n, n_cpu, seed, lambda_arg, threshold = sys.argv
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
