from __future__ import annotations
from typing import Tuple, Callable
from process import Process

class Handler:
  time: int = 0
  events = set[Tuple[int, str, Process]]()
  functions: set[Tuple[str, Process, Callable[[Handler], None]]] = set()

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
  
  def on(self, kind: str, process: Process, fn: Callable[[Handler], None]) -> None:
    self.functions.add((kind, process, fn))
  
  def off(self, kind: str, process: Process, fn: Callable[[Handler], None]) -> None:
    self.functions.remove((kind, process, fn))

  def start(self) -> None:
    self.running = True
    
    while self.running and len(self.events) > 0:
      current = min(self.events, key=lambda e: e[0])
      self.events.remove(current)
      self.time, current_kind, current_process = current

      for kind, process, fn in self.functions:
        if current_kind != kind or process != current_process: continue
        fn(self)
    
    self.running = False

  def stop(self) -> None:
    self.running = False