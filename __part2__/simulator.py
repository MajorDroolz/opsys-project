from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Callable, Union
from process import Process
from state import State
from rand48 import Event
from algorithm import Algorithm
from statistics import mean
from os import environ
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

    total_preemptions: int
    io_preemptions: int
    cpu_preemptions: int

    def __str__(self) -> str:
        return """Algorithm {}
-- CPU utilization: {:.3f}%
-- average CPU burst time: {:.3f} ms ({:.3f} ms/{:.3f} ms)
-- average wait time: {:.3f} ms ({:.3f} ms/{:.3f} ms)
-- average turnaround time: {:.3f} ms ({:.3f} ms/{:.3f} ms)
-- number of context switches: {} ({}/{})
-- number of preemptions: {} ({}/{})""".format(
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
            self.total_preemptions,
            self.io_preemptions,
            self.cpu_preemptions,
        )


@dataclass
class Simulator:
    state: State
    processes: list[Process] = field(default_factory=list)
    current: Union[Process, None] = None
    algorithm = Algorithm()

    time: int = 0
    events: list[Tuple[int, Event, Process]] = field(default_factory=list)
    functions: list[Tuple[Event, Process, Callable[[Process, Simulator], None]]] = field(
        default_factory=list
    )

    running = False

    cpu_time: int = 0
    cpu_since: int = 0

    switching: bool = False

    def reset(self) -> None:
        self.time = 0
        self.events.clear()
        self.functions = []
        self.running = False

        self.cpu_time = 0
        self.cpu_since = 0
        self.switching = False
        self.algorithm = Algorithm()
        self.current = None
        self.processes = []

    def addEvent(self, kind: Event, process: Process, wait: int = 0) -> None:
        self.events.append((wait + self.time, kind, process))

    def removeEventsFor(self, process: Process) -> None:
        self.events = sorted(e for e in self.events if e[2] != process)

    def on(
        self, kind: Event, process: Process, fn: Callable[[Process, Simulator], None]
    ) -> None:
        self.functions.append((kind, process, fn))

    def off(
        self, kind: Event, process: Process, fn: Callable[[Process, Simulator], None]
    ) -> None:
        self.functions.remove((kind, process, fn))

    def print(self, message: str, override=False) -> None:
        if not override and self.time >= 10_000 and not environ.get("ALL"):
            return
        queue_names = [p[1].name for p in self.algorithm.queue]
        if len(queue_names) == 0:
            queue_names = ["<empty>"]
        print(f"time {self.time}ms: {message} [Q {' '.join(queue_names)}]")

    def run(self, algorithm: Algorithm, header=False) -> Stats:
        self.reset()
        self.algorithm = algorithm
        self.processes = list(self.state.generate())

        [algorithm.onProcess(p, self) for p in self.processes]

        print("")

        if header:
            print(
                "<<< PROJECT PART II -- t_cs={}ms; alpha={:.2f}; t_slice={}ms >>>".format(
                    self.state.t_cs, self.state.alpha, self.state.t_slice
                )
            )

        self.print(f"Simulator started for {self.algorithm.name}")

        self.running = True

        while self.running and len(self.events) > 0:
            self.events.sort()

            self.time, current_kind, current_process = self.events.pop(0)

            for kind, process, fn in self.functions:
                if current_kind != kind or process is not current_process:
                    continue
                fn(process, self)

            if all(t != self.time for t, _, _ in self.events):
                self.algorithm.onEvented(self)

        self.print(f"Simulator ended for {self.algorithm.name}", True)
        self.running = False

        return self.stats()

    def stop(self) -> None:
        self.running = False

    def start(self) -> None:
        self.running = True

    def runProcess(self, process: Process) -> None:
        self.switching = False
        self.current = process
        self.cpu_since = self.time

    def stopProcess(self) -> None:
        self.cpu_time += self.time - self.cpu_since

    def exitProcess(self, _: Process) -> None:
        self.current = None

    def stats(self) -> Stats:
        try:
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

            total_preemptions = 0
            io_preemptions = 0
            cpu_preemptions = 0

            for s in stats:
                total_cpu_bursts += s.cpu_bursts
                total_context_switches += s.context_switches
                total_average_wait_times += s.wait_times
                total_average_ta_times += s.ta_times
                total_preemptions += s.preemptions

                if s.bound == "CPU":
                    io_cpu_bursts += s.cpu_bursts
                    io_context_switches += s.context_switches
                    io_average_wait_times += s.wait_times
                    io_average_ta_times += s.ta_times
                    io_preemptions += s.preemptions
                else:
                    cpu_cpu_bursts += s.cpu_bursts
                    cpu_context_switches += s.context_switches
                    cpu_average_wait_times += s.wait_times
                    cpu_average_ta_times += s.ta_times
                    cpu_preemptions += s.preemptions

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
                total_preemptions,
                io_preemptions,
                cpu_preemptions,
            )
        except Exception:
            return Stats("", 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
