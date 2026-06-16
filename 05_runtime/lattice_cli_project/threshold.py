class Threshold:

    def __init__(self, lattice):
        self.lattice = lattice

    def allow(self, pulse):
        return True