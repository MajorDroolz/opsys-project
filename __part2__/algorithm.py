from dataclasses import dataclass
from typing import Union, Literal, Tuple, TYPE_CHECKING
from process import Process
from queue import PriorityQueue
from math import ceil

if TYPE_CHECKING:
    from simulator import Simulator


class Algorithm:
    queue = PriorityQueue[Tuple[int, Process]]()
    name: str

    def onBegin(self, simulator: 'Simulator') -> None:
        pass

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onIO(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onExit(self, process: Process, simulator: "Simulator") -> None:
        pass

    def popNext(self) -> Union[Process, None]:
        if self.queue.empty():
            return None
        
        _, process = self.queue.get()
        self.queue.task_done()
        return process


class FCFS(Algorithm):
    name = "FCFS"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        self.queue.put((simulator.time, process))
    
    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        self.queue.put((simulator.time, process))


class SJF(Algorithm):
    name = "SJF"

    tau: int = 0

    def onBegin(self, simulator: 'Simulator') -> None:
        self.tau = ceil(1 / simulator.state.λ)

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        process.tau = self.tau
        self.queue.put((process.tau, process))

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        tau = process.tau
        t = process.bursts[process.current_burst].cpu
        alpha = simulator.state.alpha
        self.tau = ceil(alpha * t + (1 - alpha) * tau)

        process.tau = self.tau
        simulator.print(f'Recalculating tau for process {process.name}: old tau {tau}ms ==> new tau {self.tau}ms')
    
    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        self.queue.put((process.tau, process))
