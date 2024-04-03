from __future__ import annotations
from dataclasses import dataclass, field
from typing import Tuple, Callable, Union
from queue import PriorityQueue
from process import Process
from handler import Handler
from state import State
from algorithm import Algorithm


@dataclass
class Simulator:
  state: State
  processes: set[Process] = field(default_factory=set)
  queue = PriorityQueue[Tuple[int, Process]]()
  current: Union[Process, None] = None
  handler = Handler()
  algorithm = Algorithm()

  def print(self, message: str) -> None:
    queue_names = [p[1].name for p in list(self.queue.queue)]
    if len(queue_names) == 0: queue_names = ['<empty>']
    print(f"time {self.handler.time}ms: {message} [Q {' '.join(queue_names)}]")

  def run(self, algorithm: Algorithm) -> None:
    self.algorithm = algorithm
    self.processes = set(self.state.generate())

    self.print(f"Simulator started for {self.algorithm.name}")

    