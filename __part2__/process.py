from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, Literal, TYPE_CHECKING


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
    preemptions: int


@dataclass(order=True)
class Process:
    name: str
    arrival: int
    bursts: list[Burst]
    bound: Union[Literal["CPU"], Literal["I/O"]]

    current_burst: int = 0
    context_switches: int = 0

    start_wait: int = 0
    current_wait: int = 0
    wait_times: list[int] = field(default_factory=list)

    start_ta: int = 0
    ta_times: list[int] = field(default_factory=list)

    tau: int = -1

    start_cpu: int = 0
    cpu_left: int = 0
    cpu_done: int = 0

    preemptions: int = 0

    def __hash__(self) -> int:
        return hash(self.name)

    def onArrival(self, time: int) -> None:
        self.start_wait = time
        self.current_wait = 0
        self.start_ta = time
        self.cpu_left = self.bursts[self.current_burst].cpu
        self.cpu_done = 0

    def onWillCPU(self, time: int) -> None:
        self.wait_times += [(time - self.start_wait) + self.current_wait]

    def onCPU(self, time: int) -> None:
        self.context_switches += 1
        self.start_cpu = time

    def onFinishCPU(self, time: int) -> None:
        self.cpu_left -= time - self.start_cpu
        self.cpu_done += time - self.start_cpu

    def onExit(self, time: int) -> None:
        self.ta_times += [time - self.start_ta]

    def onPreempt(self, time: int) -> None:
        self.preemptions += 1
        self.current_wait += time - self.start_wait
        self.start_wait = time

    def onIO(self, time: int) -> None:
        self.ta_times += [time - self.start_ta]

    def onExpire(self, time: int) -> None:
        pass

    def onFinishIO(self, time: int) -> None:
        self.current_burst += 1
        self.cpu_left = self.bursts[self.current_burst].cpu
        self.cpu_done = 0
        self.start_wait = time
        self.current_wait = 0
        self.start_ta = time

    def stats(self) -> ProcessStats:
        return ProcessStats(
            self.bound,
            self.context_switches,
            [b.cpu for b in self.bursts],
            self.wait_times,
            self.ta_times,
            self.preemptions,
        )
