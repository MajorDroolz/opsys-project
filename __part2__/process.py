from dataclasses import dataclass
from typing import Union, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from simulator import Simulator


@dataclass
class Burst:
    cpu: int
    io: Union[int, None]
    # started: Union[float, None] = None
    # ended: Union[float, None] = None


@dataclass
class Process:
    name: str
    arrival: int
    bursts: list[Burst]
    bound: Union[Literal["CPU"], Literal["I/O"]]

    current_burst: int = 0

    def __hash__(self) -> int:
        return hash(self.name)

    def moveToCPU(self, simulator: "Simulator") -> None:
        simulator.addEvent("cpu", self, simulator.state.t_cs // 2)

    def onArrival(self, simulator: "Simulator") -> None:
        simulator.algorithm.onArrival(self, simulator)
        simulator.print(f"Process {self.name} arrived; added to ready queue")

    def onCPU(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]

        simulator.runProcess(self)
        simulator.algorithm.onCPU(self, simulator)

        simulator.addEvent("finish-cpu", self, burst.cpu)
        simulator.print(
            f"Process {self.name} started using the CPU for {burst.cpu}ms burst"
        )

    def onFinishCPU(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]

        simulator.stopProcess()
        simulator.algorithm.onFinishCPU(self, simulator)

        if burst.io is None:
            simulator.print(f"Process {self.name} terminated")
            simulator.addEvent("exit", self, simulator.state.t_cs // 2)
        else:
            simulator.addEvent("io", self, simulator.state.t_cs // 2)
            simulator.print(
                f"Process {self.name} completed a CPU burst; {len(self.bursts) - self.current_burst - 1} bursts to go"
            )
            simulator.print(
                f"Process {self.name} switching out of CPU; blocking on I/O until time {simulator.time + burst.io + simulator.state.t_cs // 2}ms"
            )

    def onExit(self, simulator: "Simulator") -> None:
        simulator.exitProcess(self)
        simulator.algorithm.onExit(self, simulator)

    def onIO(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]
        if burst.io == None:
            return

        simulator.exitProcess(self)
        simulator.algorithm.onIO(self, simulator)
        simulator.addEvent("finish-io", self, burst.io)

    def onFinishIO(self, simulator: "Simulator") -> None:
        burst = self.bursts[self.current_burst]
        self.current_burst += 1
        if burst.io == None:
            return
        simulator.algorithm.onFinishIO(self, simulator)
        simulator.print(f"Process {self.name} completed I/O; added to ready queue")

    def handle(self, simulator: "Simulator") -> None:
        simulator.on("arrival", self, self.onArrival)
        simulator.on("cpu", self, self.onCPU)
        simulator.on("finish-cpu", self, self.onFinishCPU)
        simulator.on("io", self, self.onIO)
        simulator.on("finish-io", self, self.onFinishIO)
        simulator.on("exit", self, self.onExit)

        simulator.addEvent("arrival", self, self.arrival)
