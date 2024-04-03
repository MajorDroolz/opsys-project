from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Callable, Union
from process import Process
from state import State
from algorithm import Algorithm
from statistics import mean
import math


def ceil(n: float, place: int = 0) -> float:
    return math.ceil((10**place) * n) / (10**place)


@dataclass
class Stats:
    algorithm: str
    cpu: float
    total_average_cpu_burst: float
    io_average_cpu_burst: float
    cpu_average_cpu_burst: float

    total_average_wait_time: float
    io_average_wait_time: float
    cpu_average_wait_time: float

    total_average_ta_time: float
    io_average_ta_time: float
    cpu_average_ta_time: float

    total_context_switches: int
    io_context_switches: int
    cpu_context_switches: int

    def __str__(self) -> str:
        return """Algorithm {}
-- CPU utilization: {:.3f}%
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)
-- number of context switches: {} ({}/{})
-- number of preemptions: 0 (0/0)""".format(
            self.algorithm,
            self.cpu,
            self.total_average_cpu_burst,
            self.io_average_cpu_burst,
            self.cpu_average_cpu_burst,
            self.total_average_wait_time,
            self.io_average_wait_time,
            self.cpu_average_wait_time,
            self.total_average_ta_time,
            self.io_average_ta_time,
            self.cpu_average_ta_time,
            self.total_context_switches,
            self.io_context_switches,
            self.cpu_context_switches,
        )


@dataclass
class Simulator:
    state: State
    processes: set[Process] = field(default_factory=set)
    current: Union[Process, None] = None
    algorithm = Algorithm()

    time: int = 0
    events: set[Tuple[int, str, Process]] = field(default_factory=set)
    functions: set[Tuple[str, Process, Callable[[Simulator], None]]] = field(
        default_factory=set
    )

    running = False

    cpu_time: int = 0
    cpu_since: int = 0

    def reset(self) -> None:
        self.time = 0
        self.events.clear()
        self.functions = set()
        self.running = False

        self.cpu_time = 0
        self.cpu_since = 0

    def addEvent(self, kind: str, process: Process, wait: int = 0) -> None:
        self.events.add((wait + self.time, kind, process))

    def removeEventsFor(self, process: Process) -> None:
        self.events = {e for e in self.events if e[2] != process}

    def on(self, kind: str, process: Process, fn: Callable[[Simulator], None]) -> None:
        self.functions.add((kind, process, fn))

    def off(self, kind: str, process: Process, fn: Callable[[Simulator], None]) -> None:
        self.functions.remove((kind, process, fn))

    def print(self, message: str) -> None:
        queue_names = [p[1].name for p in list(self.algorithm.queue.queue)]
        if len(queue_names) == 0:
            queue_names = ["<empty>"]
        print(f"time {self.time}ms: {message} [Q {' '.join(queue_names)}]")

    def run(self, algorithm: Algorithm) -> None:
        self.algorithm = algorithm
        self.processes = set(self.state.generate())

        [p.handle(self) for p in self.processes]

        self.print(f"Simulator started for {self.algorithm.name}")

        self.running = True

        while self.running and len(self.events) > 0:
            current = min(self.events, key=lambda e: e[0])
            self.events.remove(current)
            self.time, current_kind, current_process = current

            for kind, process, fn in self.functions:
                if current_kind != kind or process != current_process:
                    continue
                fn(self)

            if self.current is None:
                process = self.algorithm.popNext()
                if process != None:
                    process.moveToCPU(self)

        self.print(f"Simulator ended for {self.algorithm.name}")
        self.running = False

    def stop(self) -> None:
        self.running = False

    def start(self) -> None:
        self.running = True

    def runProcess(self, process: Process) -> None:
        self.current = process
        self.cpu_since = self.time

    def stopProcess(self) -> None:
        self.cpu_time += self.time - self.cpu_since

    def exitProcess(self, _: Process) -> None:
        self.current = None

    def stats(self) -> Stats:
        cpu = ceil(100 * (self.cpu_time / self.time), 3)
        stats = [p.stats() for p in self.processes]

        total_cpu_bursts = []
        io_cpu_bursts = []
        cpu_cpu_bursts = []

        total_average_wait_times = []
        io_average_wait_times = []
        cpu_average_wait_times = []

        total_average_ta_times = []
        io_average_ta_times = []
        cpu_average_ta_times = []

        total_context_switches = 0
        io_context_switches = 0
        cpu_context_switches = 0

        for s in stats:
            total_cpu_bursts += s.cpu_bursts
            total_context_switches += s.context_switches
            total_average_wait_times += s.wait_times
            total_average_ta_times += s.ta_times

            if s.bound == "CPU":
                io_cpu_bursts += s.cpu_bursts
                io_context_switches += s.context_switches
                io_average_wait_times += s.wait_times
                io_average_ta_times += s.ta_times
            else:
                cpu_cpu_bursts += s.cpu_bursts
                cpu_context_switches += s.context_switches
                cpu_average_wait_times += s.wait_times
                cpu_average_ta_times += s.ta_times

        return Stats(
            self.algorithm.name,
            cpu,
            ceil(mean(total_cpu_bursts), 3),
            ceil(mean(io_cpu_bursts), 3),
            ceil(mean(cpu_cpu_bursts), 3),
            ceil(mean(total_average_wait_times), 3),
            ceil(mean(io_average_wait_times), 3),
            ceil(mean(cpu_average_wait_times), 3),
            ceil(mean(total_average_ta_times), 3),
            ceil(mean(io_average_ta_times), 3),
            ceil(mean(cpu_average_ta_times), 3),
            total_context_switches,
            io_context_switches,
            cpu_context_switches,
        )
