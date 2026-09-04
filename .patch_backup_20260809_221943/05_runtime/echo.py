class Echo:

    def __init__(self, lattice):
        self.lattice = lattice
        self.history = []

    def record(self, result):
        self.history.append(result)