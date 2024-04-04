from __future__ import annotations
from dataclasses import dataclass, field
from typing import Union, Literal, TYPE_CHECKING

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

    def onArrival(self, time: int) -> None:
        self.start_wait = time
        self.start_ta = time

    def onWillCPU(self, time: int) -> None:
        self.wait_times += [time - self.start_wait]

    def onCPU(self, time: int) -> None:
        self.context_switches += 1

    def t(self) -> str:
        return f" (tau {self.tau}ms)" if self.tau != -1 else ""

    def onFinishCPU(self, time: int) -> None:
        pass

    def onExit(self, time: int) -> None:
        self.ta_times += [time - self.start_ta]

    def onIO(self, time: int) -> None:
        self.ta_times += [time - self.start_ta]

    def onFinishIO(self, time: int) -> None:
        self.current_burst += 1
        self.start_wait = time
        self.start_ta = time

    def stats(self) -> ProcessStats:
        return ProcessStats(
            self.bound,
            self.context_switches,
            [b.cpu for b in self.bursts],
            self.wait_times,
            self.ta_times,
        )
