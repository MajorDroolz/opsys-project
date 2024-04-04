from dataclasses import dataclass
from typing import Union, Literal, Tuple, TYPE_CHECKING
from process import Process
from queue import PriorityQueue
from math import ceil
from rand48 import Event

if TYPE_CHECKING:
    from simulator import Simulator


class Algorithm:
    queue: list[Tuple[int, Process]]
    name: str

    def __init__(self):
        self.queue = []

    def onEvented(self, simulator: "Simulator") -> None:
        if simulator.current is not None or simulator.switching:
            return
        
        process = len(self.queue) > 0 and self.queue[0] and self.queue[0][1]

        if not process:
            return

        process.onWillCPU(simulator)
        simulator.addEvent(Event.CPU, process, simulator.state.t_cs // 2)
        simulator.switching = True

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        self.queue = sorted(p for p in self.queue if p[1] is not process)

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onIO(self, process: Process, simulator: "Simulator") -> None:
        burst = process.bursts[process.current_burst]

        if burst.io == None:
            return

        simulator.exitProcess(process)
        simulator.addEvent(Event.FINISH_IO, process, burst.io)

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        pass

    def onExit(self, process: Process, simulator: "Simulator") -> None:
        simulator.exitProcess(process)


class FCFS(Algorithm):
    name = "FCFS"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        super().onArrival(process, simulator)

        self.queue.append((simulator.time, process))
        self.queue.sort()

        name = process.name
        simulator.print(f"Process {name} arrived; added to ready queue")

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        super().onCPU(process, simulator)

        cpu, name = process.bursts[process.current_burst].cpu, process.name
        simulator.runProcess(process)
        simulator.addEvent(Event.FINISH_CPU, process, cpu)
        simulator.print(f"Process {name} started using the CPU for {cpu}ms burst")

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        super().onFinishCPU(process, simulator)

        simulator.stopProcess()
        burst = process.bursts[process.current_burst]
        name = process.name

        if burst.io is None:
            simulator.print(f"Process {name} terminated", True)
            simulator.addEvent(Event.EXIT, process, simulator.state.t_cs // 2)
        else:
            bursts_left = len(process.bursts) - process.current_burst - 1
            plural = "" if bursts_left == 1 else "s"
            io_done = simulator.time + burst.io + simulator.state.t_cs // 2

            simulator.addEvent(Event.IO, process, simulator.state.t_cs // 2)
            simulator.print(
                f"Process {name} completed a CPU burst; {bursts_left} burst{plural} to go"
            )
            simulator.print(
                f"Process {name} switching out of CPU; blocking on I/O until time {io_done}ms"
            )

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        super().onArrival(process, simulator)

        self.queue.append((simulator.time, process))
        self.queue.sort()


class SJF(Algorithm):
    name = "SJF"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        process.tau = ceil(1 / simulator.state.λ)
        self.queue.append((process.tau, process))
        self.queue.sort()

        name, tau = process.name, process.tau
        simulator.print(f"Process {name} (tau {tau}ms) arrived; added to ready queue")

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        super().onCPU(process, simulator)

        cpu, name = process.bursts[process.current_burst].cpu, process.name
        tau = process.tau
        simulator.runProcess(process)
        simulator.addEvent(Event.FINISH_CPU, process, cpu)
        simulator.print(
            f"Process {name} (tau {tau}ms) started using the CPU for {cpu}ms burst"
        )

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        super().onFinishCPU(process, simulator)

        simulator.stopProcess()
        burst = process.bursts[process.current_burst]
        name = process.name

        if burst.io is None:
            simulator.print(f"Process {name} terminated", True)
            simulator.addEvent(Event.EXIT, process, simulator.state.t_cs // 2)
        else:
            bursts_left = len(process.bursts) - process.current_burst - 1
            plural = "" if bursts_left == 1 else "s"
            io_done = simulator.time + burst.io + simulator.state.t_cs // 2

            old = process.tau
            t = process.bursts[process.current_burst].cpu
            alpha = simulator.state.alpha
            new = process.tau = ceil(alpha * t + (1 - alpha) * old)

            simulator.addEvent(Event.IO, process, simulator.state.t_cs // 2)
            simulator.print(
                f"Process {name} (tau {old}ms) completed a CPU burst; {bursts_left} burst{plural} to go"
            )
            simulator.print(
                f"Recalculating tau for process {name}: old tau {old}ms ==> new tau {new}ms"
            )
            simulator.print(
                f"Process {name} switching out of CPU; blocking on I/O until time {io_done}ms"
            )

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        self.queue.append((process.tau, process))
        self.queue.sort()
