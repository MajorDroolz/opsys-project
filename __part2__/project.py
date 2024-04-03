from sys import argv
from data import Simulation
from util import ERROR


if len(argv) != 6:
    ERROR("Invalid number of parameters.")

n_processes = int(argv[1])
n_cpu = int(argv[2])
seed = int(argv[3])
λ = float(argv[4])
threshold = int(argv[5])
t_cs = int(argv[6])
alpha = float(argv[7])
t_slice = int(argv[8])

Simulation(n_processes, n_cpu, seed, λ, threshold, t_cs, alpha, t_slice).part1()
