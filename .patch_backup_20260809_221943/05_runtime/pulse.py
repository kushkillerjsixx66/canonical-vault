class Pulse:

    def __init__(self, lattice):
        self.lattice = lattice

    def activate(self, signal):
        return {"pulse": signal}