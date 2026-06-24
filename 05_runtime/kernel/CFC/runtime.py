from .types import CFCState
from .load_model import LoadModel
from .posture import PostureResolver
from .enforcer import ConstraintEnforcer


class CFCRuntime:
    """
    Crash-Free Constraints runtime.
    """

    def __init__(self):
        self.load_model = LoadModel()
        self.posture_resolver = PostureResolver()
        self.enforcer = ConstraintEnforcer()

    def run(self, ide_intent, cce_map):
        load = self.load_model.compute(
            clause_count=len(ide_intent.clauses),
            class_count=len(cce_map.classes),
        )

        posture = self.posture_resolver.resolve(load)
        enforcement = self.enforcer.enforce(posture)

        return CFCState(
            load=load,
            posture=posture,
            metadata={
                "source": "cfc",
                "altitude": ide_intent.altitude,
                "constraint_classes": cce_map.classes,
                "enforcement": enforcement,
            },
        )
