from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Callable, Union
from process import Process
from state import State
from rand48 import Event
from algorithm import Algorithm
from statistics import mean, StatisticsError
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
-- number of preemptions: {} ({}/{})\n\n""".format(
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
            self.cpu_preemptions
        )


@dataclass
class Simulator:
    state: State
    processes: set[Process] = field(default_factory=set)
    current: Union[Process, None] = None
    algorithm = Algorithm()

    time: int = 0
    events: list[Tuple[int, Event, Process]] = field(default_factory=list)
    functions: set[Tuple[Event, Process, Callable[[Process, Simulator], None]]] = field(
        default_factory=set
    )

    running = False

    cpu_time: int = 0
    cpu_since: int = 0

    switching: bool = False

    def reset(self) -> None:
        self.time = 0
        self.events.clear()
        self.functions = set()
        self.running = False

        self.cpu_time = 0
        self.cpu_since = 0
        self.switching = False
        self.algorithm = Algorithm()
        self.current = None
        self.processes = set()

    def addEvent(self, kind: Event, process: Process, wait: int = 0) -> None:
        self.events.append((wait + self.time, kind, process))

    def removeEventsFor(self, process: Process) -> None:
        self.events = sorted(e for e in self.events if e[2] != process)

    def on(
        self, kind: Event, process: Process, fn: Callable[[Process, Simulator], None]
    ) -> None:
        self.functions.add((kind, process, fn))

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
        self.processes = set(self.state.generate())

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

        while self.running and len(self.events) > 0 and self.time < 1_000_000:
            self.events.sort()
            
            self.time, current_kind, current_process = self.events.pop(0)

            for kind, process, fn in self.functions:
                if current_kind != kind or process is not current_process:
                    continue
                fn(process, self)
            
            if all(t != self.time for t,_,_ in self.events):
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
            return Stats('', 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)


# def silly(state: State):
#     print('')
#     def printp(s, t):
#         if t < 10000:
#             print(s)

#     class queue:
#         def __init__(self):
#             self.queue = []

#         def push(self, a):
#             self.queue.append(a)

#         def pop(self):
#             return self.queue.pop(0)

#         def __len__(self):
#             return len(self.queue)

#         def __str__(self):
#             if self.is_empty():
#                 return " <empty>"
#             else:
#                 return "".join([" " + x[0].name for x in self.queue])

#         def is_empty(self):
#             return len(self.queue) == 0

#     # get processes
#     processes = state.generate()

#     t = 0
#     t_context_switch = 0
#     t_slice = 0
#     t_cpu = 0

#     ready = queue()
#     running = None
#     waiting = []
#     context_switch_in = None
#     context_switch_out = None

#     last_arrival_time = max([x.arrival for x in processes])

#     io_cpu_bursts = []
#     cpu_cpu_bursts = []
#     io_preemptions = 0
#     cpu_preemptions = 0
#     io_context_switches = 0
#     cpu_context_switches = 0

#     printp("time 0ms: Simulator started for RR [Q <empty>]", t)
#     while (
#         t <= last_arrival_time
#         or not ready.is_empty()
#         or running is not None
#         or len(waiting) != 0
#         or context_switch_out is not None
#         or context_switch_in is not None
#     ):
#         # add processes to ready queue on arrival
#         for process in processes:
#             if process.arrival == t:
#                 ready.push([process, process.bursts[0].cpu])
#                 printp(
#                     f"time {t}ms: Process {process.name} arrived; added to ready queue [Q{ready}]",
#                     t,
#                 )

#         # transition out of context switch out
#         if context_switch_out is not None and t_context_switch == 0:
#             if context_switch_out[1] == 0:  # burst complete; transition to IO
#                 context_switch_out[1] = (
#                     context_switch_out[0].bursts[context_switch_out[0].current_burst].io
#                 )
#                 if context_switch_out[1] is not None:
#                     waiting.append(context_switch_out)
#             else:  # premption; transition to ready
#                 ready.push(context_switch_out)
#             context_switch_out = None

#         # context switch in --> running state
#         if context_switch_in is not None and t_context_switch == 0:
#             running = context_switch_in
#             context_switch_in = None
#             t_slice = state.t_slice
#             if running[1] == running[0].bursts[running[0].current_burst].cpu:
#                 printp(
#                     f"time {t}ms: Process {running[0].name} started using the CPU for {running[1]}ms burst [Q{ready}]",
#                     t,
#                 )
#                 if running[0].bound == "CPU":
#                     cpu_cpu_bursts.append(running[1])
#                 else:
#                     io_cpu_bursts.append(running[1])
#             else:
#                 printp(
#                     f"time {t}ms: Process {running[0].name} started using the CPU for remaining {running[1]}ms of {running[0].bursts[running[0].current_burst].cpu}ms burst [Q{ready}]",
#                     t,
#                 )
#             if running[0].bound == "CPU":
#                 cpu_context_switches += 1
#             else:
#                 io_context_switches += 1

#         # IO --> queue
#         for process in reversed(waiting):
#             if process[1] == 0:
#                 process[0].current_burst += 1
#                 process[1] = process[0].bursts[process[0].current_burst].cpu
#                 ready.push(process)
#                 printp(
#                     f"time {t}ms: Process {process[0].name} completed I/O; added to ready queue [Q{ready}]",
#                     t,
#                 )
#                 waiting.remove(process)
#             elif process[1] < 0:
#                 raise Exception("negative t")
#             else:
#                 process[1] -= 1

#         # ready queue --> context switch in
#         if running is None and t_context_switch == 0 and not ready.is_empty():
#             context_switch_in = ready.pop()
#             t_context_switch = state.t_cs / 2

#         if running is not None:
#             # switch process out of running if burst is completed
#             if running[1] == 0:
#                 if running[0].current_burst + 1 == len(running[0].bursts):
#                     context_switch_out = running
#                     print(
#                         f"time {t}ms: Process {running[0].name} terminated [Q{ready}]"
#                     )
#                     # if not ready.is_empty():
#                     #     running = None
#                     #     context_switch_in = ready.pop()
#                     #     t_context_switch = state.t_cs / 2
#                     # else:
#                     #     running = None
#                     running = None
#                     t_context_switch = state.t_cs / 2

#                 else:
#                     context_switch_out = running
#                     printp(
#                         f"time {t}ms: Process {running[0].name} completed a CPU burst; {len(running[0].bursts) - running[0].current_burst} bursts to go [Q{ready}]",
#                         t,
#                     )
#                     printp(
#                         f"time {t}ms: Process {running[0].name} switching out of CPU; blocking on I/O until time {t + running[0].bursts[running[0].current_burst].io + int(state.t_cs / 2)}ms [Q{ready}]",
#                         t,
#                     )
#                     running = None
#                     t_context_switch = state.t_cs / 2

#             # switch process out of running in case of pre-emption --> context out
#             elif t_slice == 0:
#                 if ready.is_empty():
#                     t_slice = state.t_slice
#                     printp(
#                         f"time {t}ms: Time slice expired; no preemption because ready queue is empty [Q <empty>]",
#                         t,
#                     )
#                     running[1] -= 1
#                 else:
#                     printp(
#                         f"time {t}ms: Time slice expired; preempting process {running[0].name} with {running[1]}ms remaining [Q{ready}]",
#                         t,
#                     )
#                     if running[0].bound == "CPU":
#                         cpu_preemptions += 1
#                     else:
#                         io_preemptions += 1
#                     context_switch_out = running
#                     running = None
#                     t_context_switch = state.t_cs / 2

#             else:
#                 running[1] -= 1

#         # update time values
#         if running is not None:
#             t_cpu += 1
#         t_context_switch = max(t_context_switch - 1, 0)
#         t_slice = max(t_slice - 1, 0)
#         t += 1
#     print(f"time {t - 1}ms: Simulator ended for RR [Q <empty>]")
#     return Stats(
#         "RR",
#         ceil(100 * (t_cpu / (t - 1)), 3),
#         ceil(mean(io_cpu_bursts + cpu_cpu_bursts), 3),
#         ceil(mean(cpu_cpu_bursts), 3),
#         ceil(mean(io_cpu_bursts), 3),
#         1,
#         1,
#         1,
#         1,
#         1,
#         1,
#         cpu_context_switches + io_context_switches,
#         cpu_context_switches,
#         io_context_switches,
#         cpu_preemptions + io_preemptions,
#         cpu_preemptions,
#         io_preemptions,
#     )
