from sys import argv
from state import State, c_float
from simulator import Simulator
from algorithm import FCFS, SJF, SRT, RR


try:
    if len(argv) != 9:
        raise Exception()

    n_processes = int(argv[1])

    if n_processes < 0 or n_processes > 26:
        raise Exception()

    n_cpu = int(argv[2])

    if n_cpu < 0 or n_cpu > n_processes:
        raise Exception()

    seed = int(argv[3])
    λ = float(argv[4])
    threshold = int(argv[5])
    t_cs = int(argv[6])

    if t_cs < 0 or t_cs % 2 == 1:
        raise Exception()

    alpha = c_float(float(argv[7]))
    t_slice = int(argv[8])

    if t_slice < 0:
        raise Exception
except:
    print(f"ERROR: Invalid number of parameters.")
    exit(1)

state = State(n_processes, n_cpu, seed, λ, threshold, t_cs, alpha, t_slice)

# Part 1
processes = state.generate()
print(state.toString(processes))

# Part 2
simulator = Simulator(state)

try:
    fcfs = simulator.run(FCFS(), header=True)
except:
    fcfs = simulator.stats()

try:
    sjf = simulator.run(SJF())
except:
    sjf = simulator.stats()

try:
    srt = simulator.run(SRT())
except:
    srt = simulator.stats()

try:
    rr = simulator.run(RR())
except:
    rr = simulator.stats()

simout = open("simout.txt", "w")
simout.write(str(fcfs))
simout.write(str(sjf))
simout.write(str(srt))
simout.write(str(rr))
