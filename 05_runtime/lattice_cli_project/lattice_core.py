from agent import Agent
from sentinel import Sentinel
from pulse import Pulse
from echo import Echo
from threshold import Threshold
from veil import Veil
from rift import Rift
from stumpy import Stumpy
from vara import Vara
from vault import Vault

class Lattice:

    def __init__(self):
        self.vault = Vault()
        self.agent = Agent(self)
        self.sentinel = Sentinel(self)
        self.pulse = Pulse(self)
        self.echo = Echo(self)
        self.threshold = Threshold(self)
        self.veil = Veil(self)
        self.rift = Rift(self)
        self.stumpy = Stumpy(self)
        self.vara = Vara(self)

    def process(self, signal):

        if not self.sentinel.inspect(signal):
            return None

        pulse = self.pulse.activate(signal)

        if not self.threshold.allow(pulse):
            return None

        protected = self.veil.filter(pulse)
        exploration = self.vara.expand(protected)
        result = self.agent.act(exploration)

        self.echo.record(result)
        self.vault.store(result)
        self.stumpy.audit(result)

        return result