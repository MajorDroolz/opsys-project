import math


# Exact algorithm suite in `glibc`.
# Credit to Dietrich Epp on Stack Overflow.
# https://stackoverflow.com/a/7287046
class Rand48(object):
    def __init__(self, seed, lambda_arg=0.001, threshold=3000):
        self.n = seed
        self.lambda_arg = lambda_arg
        self.threshold = threshold

    def seed(self, seed):
        self.n = seed

    def srand(self, seed):
        self.n = (seed << 16) + 0x330E

    def next(self):
        self.n = (25214903917 * self.n + 11) & (2**48 - 1)
        return self.n

    def drand(self):
        return self.next() / 2**48

    def lrand(self):
        return self.next() >> 17

    def mrand(self):
        n = self.next() >> 16
        if n & (1 << 31):
            n -= 1 << 32
        return n

    # custom implementation of next_exp
    def next_exp(self):
        value = -math.log(self.drand()) / self.lambda_arg
        if value > self.threshold:
            return self.next_exp()
        else:
            return value


if __name__ == "__main__":
    # Create random object.
    random = Rand48(0)

    # Testing code.
    for i in range(100):
        random.srand(i)

        for j in range(100):
            print("%.10f" % random.drand())

        print()
