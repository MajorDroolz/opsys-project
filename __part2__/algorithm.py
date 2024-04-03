from dataclasses import dataclass
from typing import Union, Literal, Tuple, TYPE_CHECKING
from process import Process
from queue import PriorityQueue

if TYPE_CHECKING:
    from simulator import Simulator


class Algorithm:
    queue = PriorityQueue[Tuple[int, Process]]()
    name: str

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
