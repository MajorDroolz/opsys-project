from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, Literal, TYPE_CHECKING
from rand48 import Event

if TYPE_CHECKING:
    from simulator import Simulator

@dataclass
class Burst:
    cpu: int
    io: Union[int, None]


@dataclass
class ProcessStats:
    bound: Union[Literal["CPU"], Literal["I/O"]]
    context_switches: int
    cpu_bursts: list[int]
    wait_times: list[int]
    ta_times: list[int]


@dataclass(order=True)
class Process:
    name: str
    arrival: int
    bursts: list[Burst]
    bound: Union[Literal["CPU"], Literal["I/O"]]

    current_burst: int = 0
    context_switches: int = 0

    start_wait: int = 0
    wait_times: list[int] = field(default_factory=list)

    start_ta: int = 0
    ta_times: list[int] = field(default_factory=list)

    tau: int = -1

    def __hash__(self) -> int:
        return hash(self.name)

    def moveToCPU(self, simulator: "Simulator", ms: Union[int, None] = None) -> None:
        time = ms if ms is not None else simulator.state.t_cs // 2
        self.wait_times += [simulator.time - self.start_wait]
        simulator.addEvent(Event.CPU, self, time)

    def onArrival(self, simulator: "Simulator") -> None:
        self.start_wait = simulator.time
        self.start_ta = simulator.time
        simulator.algorithm.onArrival(self, simulator)
        simulator.print(f"Process {self.name}{self.t()} arrived; added to ready queue")

    def onCPU(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]

        simulator.runProcess(self)
        self.context_switches += 1
        simulator.algorithm.onCPU(self, simulator)

        simulator.addEvent(Event.FINISH_CPU, self, burst.cpu)
        simulator.print(
            f"Process {self.name}{self.t()} started using the CPU for {burst.cpu}ms burst"
        )

    def t(self) -> str:
        return f" (tau {self.tau}ms)" if self.tau != -1 else ""

    def onFinishCPU(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]

        simulator.stopProcess()

        if burst.io is None:
            simulator.print(f"Process {self.name} terminated", True)
            simulator.addEvent(Event.EXIT, self, simulator.state.t_cs // 2)
        else:
            simulator.addEvent(Event.IO, self, simulator.state.t_cs // 2)
            simulator.print(
                f"Process {self.name}{self.t()} completed a CPU burst; {len(self.bursts) - self.current_burst - 1} burst{'' if len(self.bursts) - self.current_burst - 1 == 1 else 's'} to go"
            )
            simulator.algorithm.onFinishCPU(self, simulator)
            simulator.print(
                f"Process {self.name} switching out of CPU; blocking on I/O until time {simulator.time + burst.io + simulator.state.t_cs // 2}ms"
            )

    def onExit(self, simulator: "Simulator") -> None:
        simulator.exitProcess(self)
        self.ta_times += [simulator.time - self.start_ta]
        simulator.algorithm.onExit(self, simulator)

    def onIO(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]
        if burst.io == None:
            return

        simulator.exitProcess(self)
        self.ta_times += [simulator.time - self.start_ta]
        simulator.algorithm.onIO(self, simulator)
        simulator.addEvent(Event.FINISH_IO, self, burst.io)

    def onFinishIO(self, simulator: "Simulator") -> None:
        # if simulator.time >= 266393:
        #     print("", end='')
        burst = self.bursts[self.current_burst]
        self.current_burst += 1
        if burst.io == None:
            return
        simulator.algorithm.onFinishIO(self, simulator)
        self.start_wait = simulator.time
        self.start_ta = simulator.time
        simulator.print(
            f"Process {self.name}{self.t()} completed I/O; added to ready queue"
        )

    def handle(self, simulator: "Simulator") -> None:
        simulator.on(Event.ARRIVAL, self, self.onArrival)
        simulator.on(Event.CPU, self, self.onCPU)
        simulator.on(Event.FINISH_CPU, self, self.onFinishCPU)
        simulator.on(Event.IO, self, self.onIO)
        simulator.on(Event.FINISH_IO, self, self.onFinishIO)
        simulator.on(Event.EXIT, self, self.onExit)

        simulator.addEvent(Event.ARRIVAL, self, self.arrival)

    def stats(self) -> ProcessStats:
        return ProcessStats(
            self.bound,
            self.context_switches,
            [b.cpu for b in self.bursts],
            self.wait_times,
            self.ta_times,
        )
