from randomc.random import Rand48
import math
import os
import sys

alphabet = "ABCDEFGHIJKLMNOPQRSTUV"


# 1
def arrival(random):
    return math.floor(random.next_exp())


# 2
def bursts(random):
    return math.ceil(random.drand() * 64)


# 3
def generate_process(n, random):
    processes = []
    for _ in range(n):
        process = {}
        process["arrival_time"] = arrival()
        process["cpu_bursts"] = bursts()
        process["bursts"] = []
        for i in range(process["cpu_bursts"]):
            cpu_burst_time = math.ceil(random.next_exp())
            io_burst_time = math.ceil(random.next_exp()) * 10
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

    # parse args
    n = int(sys.argv[1])
    n_cpu = int(sys.argv[2])
    seed = int(sys.argv[3])
    lambda_arg = float(sys.argv[4])
    threshold = int(sys.argv[5])

    # initialize random number generator
    random = Rand48(0, lambda_arg, threshold)
    random.srand(seed)
    print(
        f"<<< PROJECT PART I -- process set (n={n}) with {n_cpu} CPU-bound process >>>"
    )
    for i in range(n - n_cpu):
        num_bursts = bursts(random)
        print(
            f"I/O-bound process {alphabet[i]}: arrival time {arrival(random)}ms; {num_bursts} CPU bursts:"
        )
        # for burst in range(num_bursts - 1):
        #     print(f"--> CPU burst {}ms --> I/O burst {}ms")
        # print(f"--> CPU burst {}ms")

    for i in range(n - n_cpu, n):
        num_bursts = bursts(random)
        print(
            f"CPU-bound process {alphabet[i]}: arrival time {arrival(random)}ms; {num_bursts} CPU bursts:"
        )
        # for burst in range(num_bursts - 1):
        #     print(f"--> CPU burst {}ms --> I/O burst {}ms")
        # print(f"--> CPU burst {}ms")
