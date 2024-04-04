from math import log
from enum import IntEnum


class Event(IntEnum):
    FINISH_CPU = 1
    CPU = 2
    FINISH_IO = 3
    IO = 4
    PREEMPT = 5
    ARRIVAL = 6
    EXIT = 7
    EXPIRE = 8


# Exact algorithm suite in `glibc`.
# Credit to Dietrich Epp on Stack Overflow.
# https://stackoverflow.com/a/7287046
class Rand48(object):
    def __init__(self, seed: int) -> None:
        self.n = seed

    def seed(self, seed: int) -> None:
        self.n = seed

    def srand(self, seed: int) -> None:
        self.n = (seed << 16) + 0x330E

    def next(self) -> int:
        self.n = (25214903917 * self.n + 11) & (2**48 - 1)
        return self.n

    def drand(self) -> float:
        return self.next() / 2**48

    def lrand(self) -> int:
        return self.next() >> 17

    def mrand(self) -> int:
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

    def next_exp(self, λ: float, threshold: int) -> float:
        r = self.drand()
        x = -log(r) / λ
        return x if x < threshold else self.next_exp(λ, threshold)
