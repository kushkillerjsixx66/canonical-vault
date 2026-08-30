class Agent:

    def __init__(self, lattice):
        self.lattice = lattice

    def act(self, signal):
        return {"agent_output": signal}