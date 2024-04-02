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

print(Simulation(n_processes, seed, λ, threshold, n_cpu), end="")
