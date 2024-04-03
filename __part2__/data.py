from dataclasses import dataclass
from typing import Union, Literal
from rand48 import Rand48
from util import ERROR
from math import floor, ceil


@dataclass
class Burst:
    """
    A singular burst in a process.
    """

    cpu: int
    io: Union[int, None]


@dataclass
class Process:
    name: str
    arrival: int
    bursts: list[Burst]
    bound: Union[Literal["CPU"], Literal["I/O"]]


@dataclass
class Simulation:
    n_processes: int
    n_cpu: int
    seed: int
    λ: float
    threshold: int
    t_cs: int
    alpha: float
    t_slice: int
    processes: list[Process] = []
    n_io: int = 0

    def __post_init__(self):
        self.processes = self.generate()
        self.n_io = self.n_processes - self.n_cpu

    def generate(self) -> list[Process]:
        rand = Rand48(0)
        rand.srand(self.seed)

        names = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        processes = []

        for i in range(self.n_processes):
            name = names[i]
            arrival = floor(rand.next_exp(self.λ, self.threshold))
            n_bursts = ceil(64 * rand.drand())
            bursts = []
            bound = "CPU" if i >= self.n_io else "I/O"

            for j in range(n_bursts):
                cpu = ceil(rand.next_exp(self.λ, self.threshold))
                io = None

                if j != n_bursts - 1:
                    io = 10 * ceil(rand.next_exp(self.λ, self.threshold))

                    if bound == "CPU":
                        io //= 8

                if bound == "CPU":
                    cpu *= 4

                bursts.append(Burst(cpu, io))

            processes.append(Process(name, arrival, bursts, bound))

        return processes

    def part1(self) -> None:
        print(
            f"<<< PROJECT PART I -- process set (n={self.n_processes}) with {self.n_cpu} CPU-bound process{'' if self.n_cpu == 1 else 'es'} >>>"
        )
        for p in self.processes:
            print(
                f"{p.bound}-bound process {p.name}: arrival time {p.arrival}ms; {len(p.bursts)} CPU burst{'' if len(p.bursts) == 1 else 's'}:",
                end="",
            )
            for b in p.bursts:
                if b.io is not None:
                    print(f"--> CPU burst {b.cpu}ms --> I/O burst {b.io}ms", end="")
                else:
                    print(f"--> CPU burst {b.cpu}ms", end="")
