from sys import argv
from state import State
from simulator import Simulator
from algorithm import FCFS


if len(argv) != 9:
    print(f"ERROR: Invalid number of parameters.")
    exit(1)

n_processes = int(argv[1])
n_cpu = int(argv[2])
seed = int(argv[3])
λ = float(argv[4])
threshold = int(argv[5])
t_cs = int(argv[6])
alpha = float(argv[7])
t_slice = int(argv[8])

state = State(n_processes, n_cpu, seed, λ, threshold, t_cs, alpha, t_slice)

# Part 1
processes = state.generate()
state.print(processes)

# Part 2
simulator = Simulator(state)
simulator.run(FCFS())