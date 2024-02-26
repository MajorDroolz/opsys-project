class drand48:
  def __init__(self, seed=0):
    self.state = seed & 0xFFFFFFFFFFFF  # Ensure seed is 48-bit

  def rand(self):
    self.state = (0x5DEECE66D * self.state + 0xB) & 0xFFFFFFFFFFFF
    return self.state / 0x1000000000000  # Scale to [0, 1)
  
for i in range(100):
  rand = drand48(i)
  for j in range(100):
    print("%.10f" % rand.rand())
