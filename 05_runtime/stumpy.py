class Stumpy:

    def __init__(self, lattice):
        self.lattice = lattice
        self.invariants = [
            "coherence",
            "attention_cost",
            "reversibility",
            "silence",
            "entropy"
        ]

    def audit(self, result):
        report = {}
        for invariant in self.invariants:
            report[invariant] = invariant in result
        return report