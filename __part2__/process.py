from dataclasses import dataclass
from typing import Union, Literal

@dataclass
class Burst:
    cpu: int
    io: Union[int, None]
    started: Union[float, None] = None
    ended: Union[float, None] = None

@dataclass
class Process:
    name: str
    arrival: int
    bursts: list[Burst]
    bound: Union[Literal["CPU"], Literal["I/O"]]

    def __hash__(self) -> int:
      return hash(self.name)