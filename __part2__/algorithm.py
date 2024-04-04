from typing import Tuple, TYPE_CHECKING
from process import Process
from math import ceil
from rand48 import Event
from state import c_float

if TYPE_CHECKING:
    from simulator import Simulator


class Algorithm:
    queue: list[Tuple[int, Process]]
    name: str

    def __init__(self):
        self.queue = []

    def onProcess(self, process: Process, simulator: "Simulator") -> None:
        simulator.on(Event.ARRIVAL, process, self.onArrival)
        simulator.on(Event.CPU, process, self.onCPU)
        simulator.on(Event.FINISH_CPU, process, self.onFinishCPU)
        simulator.on(Event.IO, process, self.onIO)
        simulator.on(Event.FINISH_IO, process, self.onFinishIO)
        simulator.on(Event.EXIT, process, self.onExit)
        simulator.on(Event.PREEMPT, process, self.onPreempt)
        simulator.on(Event.EXPIRE, process, self.onExpire)

        simulator.addEvent(Event.ARRIVAL, process, process.arrival)

    def onEvented(self, simulator: "Simulator") -> bool:
        if simulator.current is not None or simulator.switching:
            return False

        process = len(self.queue) > 0 and self.queue[0] and self.queue[0][1]

        if not process:
            return False

        self.queue = [p for p in self.queue if p[1] is not process]
        process.onWillCPU(simulator.time)
        simulator.addEvent(Event.CPU, process, simulator.state.t_cs // 2)
        simulator.switching = True

        return True

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        process.onArrival(simulator.time)

    def onPreempt(self, process: Process, simulator: "Simulator") -> None:
        process.onPreempt(simulator.time)

    def onExpire(self, process: Process, simulator: "Simulator") -> None:
        process.onExpire(simulator.time)

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        process.onCPU(simulator.time)

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        process.onFinishCPU(simulator.time)

    def onIO(self, process: Process, simulator: "Simulator") -> None:
        process.onIO(simulator.time)

        burst = process.bursts[process.current_burst]

        if burst.io == None:
            return

        simulator.exitProcess(process)
        simulator.addEvent(Event.FINISH_IO, process, burst.io)

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        process.onFinishIO(simulator.time)

    def onExit(self, process: Process, simulator: "Simulator") -> None:
        process.onExit(simulator.time)

        simulator.exitProcess(process)


class FCFS(Algorithm):
    name = "FCFS"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        super().onArrival(process, simulator)

        self.queue.append((simulator.time, process))

        name = process.name
        simulator.print(f"Process {name} arrived; added to ready queue")

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        super().onCPU(process, simulator)

        cpu, name = process.bursts[process.current_burst].cpu, process.name
        simulator.runProcess(process)
        simulator.addEvent(Event.FINISH_CPU, process, process.cpu_left)

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
        super().onFinishIO(process, simulator)

        self.queue.append((simulator.time, process))

        simulator.print(f"Process {process.name} completed I/O; added to ready queue")


class SJF(Algorithm):
    name = "SJF"

    def onArrival(self, process: Process, simulator: "Simulator") -> None:
        super().onArrival(process, simulator)

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
        simulator.addEvent(Event.FINISH_CPU, process, process.cpu_left)
        if process.cpu_left != cpu:
            simulator.print(
                f"Process {name} (tau {tau}ms) started using the CPU for remaining {process.cpu_left}ms of {cpu}ms burst"
            )
        else:
            simulator.print(
                f"Process {name} (tau {tau}ms) started using the CPU for {cpu}ms burst"
            )

    def onFinishCPU(self, process: Process, simulator: "Simulator") -> None:
        if super().onFinishCPU(process, simulator):
            return

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
            new = process.tau = ceil(c_float(alpha * t) + c_float((1 - alpha) * old))

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
        super().onFinishIO(process, simulator)

        self.queue.append((process.tau, process))
        self.queue.sort()

        name, tau = process.name, process.tau
        simulator.print(
            f"Process {name} (tau {tau}ms) completed I/O; added to ready queue"
        )


class SRT(SJF):
    name = "SRT"

    def onEvented(self, simulator: "Simulator") -> None:
        super().onEvented(simulator)

        current, time = simulator.current, simulator.time

        if current is None or simulator.switching or len(self.queue) == 0:
            return

        process = self.queue[0][1]

        curr_left = current.tau - current.cpu_done
        curr_cpu = time - current.start_cpu
        true_curr_left = curr_left - curr_cpu

        best_left = process.tau - process.cpu_done
        
        if true_curr_left <= best_left:
            return

        simulator.removeEventsFor(current)

        simulator.stopProcess()
        simulator.addEvent(Event.PREEMPT, current, simulator.state.t_cs // 2)
        current.onFinishCPU(simulator.time)

        simulator.print(
            f'Process {process.name} (tau {process.tau}ms) will preempt {current.name}'
        )

    def onPreempt(self, process: Process, simulator: "Simulator") -> None:
        super().onPreempt(process, simulator)

        simulator.exitProcess(process)
        self.queue.append((process.tau - process.cpu_done, process))
        self.queue.sort()

        simulator.switching = False

    def onFinishIO(self, process: Process, simulator: "Simulator") -> None:
        process.onFinishIO(simulator.time)

        name, tau = process.name, process.tau
        curr, time = simulator.current, simulator.time

        self.queue.append((process.tau, process))
        self.queue.sort()

        if curr is not None and not simulator.switching and (curr.tau - curr.cpu_done) - (time - curr.start_cpu) > tau:
            simulator.removeEventsFor(curr)

            simulator.stopProcess()
            simulator.addEvent(Event.PREEMPT, curr, simulator.state.t_cs // 2)
            curr.onFinishCPU(simulator.time)
            simulator.switching = True

            simulator.print(
                f'Process {name} (tau {tau}ms) completed I/O; preempting {curr.name}'
            )
        else:
            simulator.print(
                f"Process {name} (tau {tau}ms) completed I/O; added to ready queue"
            )

class RR(FCFS):
    name = "RR"
    counter = 1

    def onPreempt(self, process: Process, simulator: "Simulator") -> None:
        super().onPreempt(process, simulator)

        simulator.exitProcess(process)
        self.queue.append((simulator.time, process))

        simulator.switching = False

    def onExpire(self, process: Process, simulator: "Simulator") -> None:
        if len(self.queue) == 0:
            process.onFinishCPU(simulator.time)
            process.start_cpu = simulator.time

            simulator.print(f"Time slice expired; no preemption because ready queue is empty")

            if process.cpu_left <= simulator.state.t_slice:
                simulator.addEvent(Event.FINISH_CPU, process, process.cpu_left)
            else:
                simulator.addEvent(Event.EXPIRE, process, simulator.state.t_slice)
            
            return

        super().onExpire(process, simulator)

        simulator.removeEventsFor(process)
        simulator.stopProcess()
        simulator.addEvent(Event.PREEMPT, process, simulator.state.t_cs // 2)
        process.onFinishCPU(simulator.time)
        simulator.switching = True

        time_left = process.bursts[process.current_burst].cpu - process.cpu_done
        simulator.print(
            f'Time slice expired; preempting process {process.name} with {time_left}ms remaining'
        )

    def onCPU(self, process: Process, simulator: "Simulator") -> None:
        process.onCPU(simulator.time)

        cpu, name = process.bursts[process.current_burst].cpu, process.name
        simulator.runProcess(process)

        if process.cpu_left <= simulator.state.t_slice:
            simulator.addEvent(Event.FINISH_CPU, process, process.cpu_left)
        else:
            simulator.addEvent(Event.EXPIRE, process, simulator.state.t_slice)

        if process.cpu_done == 0:
            simulator.print(f"Process {name} started using the CPU for {cpu}ms burst")
        else:
            simulator.print(f"Process {name} started using the CPU for remaining {process.cpu_left}ms of {cpu}ms burst")