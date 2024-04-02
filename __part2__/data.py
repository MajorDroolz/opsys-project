from dataclasses import dataclass
from typing import Union, Literal
from rand48 import Rand48
from util import ERROR
from math import floor, ceil


BOUNDTYPE = Union[Literal["CPU"], Literal["I/O"]]


@dataclass
class Burst:
    """
    A singular burst in a process.
    """

    cpu: int
    io: Union[int, None]

    def __init__(self, cpu: int, io: Union[int, None]) -> None:
        self.cpu = cpu
        self.io = io

    def __str__(self):
        if self.io is not None:
            return f"--> CPU burst {self.cpu}ms --> I/O burst {self.io}ms"
        else:
            return f"--> CPU burst {self.cpu}ms"


@dataclass
class Process:
    name: str
    arrival: int
    bursts: list[Burst]
    bound: BOUNDTYPE

    def __init__(self, name: str, arrival: int, bursts: list[Burst], bound: BOUNDTYPE):
        self.name = name
        self.arrival = arrival
        self.bursts = bursts
        self.bound = bound

    def __str__(self) -> str:
        result = f"{self.bound}-bound process {self.name}: arrival time {self.arrival}ms; {len(self.bursts)} CPU burst{'' if len(self.bursts) == 1 else 's'}:"
        for b in self.bursts:
            result += f"\n{b}"

        return result


@dataclass
class Simulation:
    n_processes: int
    seed: int
    λ: float
    bound: int
    n_cpu: int
    n_io: int
    processes: list[Process]
    t_cs: int
    alpha: float
    t_slice: int

    def __init__(
        self,
        n_processes: int,
        seed: int,
        λ: float,
        threshold: int,
        n_cpu: int,
        t_cs: int,
        alpha: float,
        t_slice: int,
    ):
        self.n_processes = n_processes
        self.seed = seed
        self.λ = λ
        self.threshold = threshold
        self.n_cpu = n_cpu
        self.n_io = n_processes - n_cpu

        self.t_cs = t_cs
        self.alpha = alpha
        self.t_slice = t_slice

        self.processes = self.generate()

    def generate(self) -> list[Process]:
        rand = Rand48(0)
        rand.srand(self.seed)

        names = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
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

    def __str__(self) -> str:
        result = f"<<< PROJECT PART I -- process set (n={self.n_processes}) with {self.n_cpu} CPU-bound process{'' if self.n_cpu == 1 else 'es'} >>>"
        for p in self.processes:
            result += f"\n{p}"

        result += f"<<< PROJECT PART II -- t_cs={self.t_cs}ms; alpha={self.alpha}; t_slice={self.t_slice}ms >>>"
        return result
