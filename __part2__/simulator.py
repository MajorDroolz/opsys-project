from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Callable, Union
from queue import PriorityQueue
from process import Process
from state import State
from algorithm import Algorithm


@dataclass
class Simulator:
    state: State
    processes: set[Process] = field(default_factory=set)
    queue = PriorityQueue[Tuple[int, Process]]()
    current: Union[Process, None] = None
    algorithm = Algorithm()

    time: int = 0
    events: set[Tuple[int, str, Process]] = field(default_factory=set)
    functions: set[Tuple[str, Process, Callable[[Simulator], None]]] = field(default_factory=set)

    running = False

    def reset(self) -> None:
        self.time = 0
        self.events.clear()
        self.functions = set()
        self.running = False

    def addEvent(self, kind: str, process: Process, wait: int = 0) -> None:
        self.events.add((wait + self.time, kind, process))

    def removeEventsFor(self, process: Process) -> None:
        self.events = {e for e in self.events if e[2] != process}

    def on(self, kind: str, process: Process, fn: Callable[[Simulator], None]) -> None:
        self.functions.add((kind, process, fn))

    def off(self, kind: str, process: Process, fn: Callable[[Simulator], None]) -> None:
        self.functions.remove((kind, process, fn))

    def print(self, message: str) -> None:
        queue_names = [p[1].name for p in list(self.queue.queue)]
        if len(queue_names) == 0:
            queue_names = ["<empty>"]
        print(f"time {self.time}ms: {message} [Q {' '.join(queue_names)}]")

    def run(self, algorithm: Algorithm) -> None:
        self.algorithm = algorithm
        self.processes = set(self.state.generate())

        [p.handle(self) for p in self.processes]

        self.print(f"Simulator started for {self.algorithm.name}")

        self.running = True

        while self.running and len(self.events) > 0:
            current = min(self.events, key=lambda e: e[0])
            self.events.remove(current)
            self.time, current_kind, current_process = current

            for kind, process, fn in self.functions:
                if current_kind != kind or process != current_process:
                    continue
                fn(self)

        self.running = False

    def stop(self) -> None:
        self.running = False

    def start(self) -> None:
        self.running = True
