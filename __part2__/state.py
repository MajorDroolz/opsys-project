from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple, Callable, Union
from process import Process
from handler import Handler
from rand48 import Rand48
from dataclasses import dataclass
from rand48 import Rand48
from math import floor, ceil
from process import Process, Burst


@dataclass
class State:
    n_processes: int
    n_cpu: int
    seed: int
    λ: float
    threshold: int
    t_cs: int
    alpha: float
    t_slice: int
    n_io: int = 0

    def __post_init__(self) -> None:
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

    def print(self, processes: list[Process]) -> None:
        print(
            f"<<< PROJECT PART I -- process set (n={self.n_processes}) with {self.n_cpu} CPU-bound process{'' if self.n_cpu == 1 else 'es'} >>>"
        )
        for p in processes:
            print(
                f"{p.bound}-bound process {p.name}: arrival time {p.arrival}ms; {len(p.bursts)} CPU burst{'' if len(p.bursts) == 1 else 's'}:"
            )
            for b in p.bursts:
                if b.io is not None:
                    print(f"--> CPU burst {b.cpu}ms --> I/O burst {b.io}ms")
                else:
                    print(f"--> CPU burst {b.cpu}ms")
