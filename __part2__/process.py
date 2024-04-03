from dataclasses import dataclass
from typing import Union, Literal, TYPE_CHECKING

if TYPE_CHECKING:
    from simulator import Simulator


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

    def onArrival(self, simlator: 'Simulator') -> None:
        simlator.print(f"Process {self.name} arrived; added to ready queue")

    def handle(self, simlator: 'Simulator') -> None:
        simlator.on("arrival", self, self.onArrival)
        simlator.addEvent("arrival", self, self.arrival)
