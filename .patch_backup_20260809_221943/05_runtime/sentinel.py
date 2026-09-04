class Sentinel:

    def __init__(self, lattice):
        self.lattice = lattice

    def inspect(self, signal):
        return signal is not None