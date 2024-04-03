from dataclasses import dataclass
from typing import Union, Literal, Tuple, TYPE_CHECKING
from process import Process
from queue import PriorityQueue
from math import ceil

if TYPE_CHECKING:
    from simulator import Simulator


class Algorithm:
    queue: list[Tuple[int, Process]]
    name: str

    def __init__(self ):
        self.queue = []

    def onBegin(self, simulator: 'Simulator') -> None:
        pass

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        self.queue = sorted(p for p in self.queue if p[1] is not process)

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onIO(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onExit(self, process: Process, simulator: "Simulator") -> None:
        pass

    def next(self) -> Union[Process, None]:
        if len(self.queue) == 0:
            return None
        
        _, process = self.queue[0]
        return process


class FCFS(Algorithm):
    name = "FCFS"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        self.queue.append((simulator.time, process))
        self.queue.sort()
    
    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        self.queue.append((simulator.time, process))
        self.queue.sort()


class SJF(Algorithm):
    name = "SJF"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        process.tau = ceil(1 / simulator.state.λ)
        self.queue.append((process.tau, process))
        self.queue.sort()

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        tau = process.tau
        t = process.bursts[process.current_burst].cpu
        alpha = simulator.state.alpha

        process.tau = ceil(alpha * t + (1 - alpha) * tau)
        simulator.print(f'Recalculating tau for process {process.name}: old tau {tau}ms ==> new tau {process.tau}ms')
    
    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        self.queue.append((process.tau, process))
        self.queue.sort()

class SRT(Algorithm):
    name = "SRT"
    tau: int = 0

    def onBegin(self, simulator: 'Simulator') -> None:
        self.tau = ceil(1 / simulator.state.λ)

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        process.tau = self.tau
        self.queue.append((process.tau, process))
        self.queue.sort()

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        self.queue.remove((process.tau, process))
        tau = process.tau
        t = process.bursts[process.current_burst].cpu
        alpha = simulator.state.alpha
        self.tau = ceil(alpha * t) + ceil((1 - alpha) * tau)

        process.tau = self.tau
        self.queue.append((process.tau, process))
        self.queue.sort()
        simulator.print(f'Recalculating tau for process {process.name}: old tau {tau}ms ==> new tau {self.tau}ms')
    
    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        self.queue.append((process.tau, process))
        self.queue.sort()