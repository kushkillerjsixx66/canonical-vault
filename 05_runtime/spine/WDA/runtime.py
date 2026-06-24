from .policy import AuditPolicy
from .evaluator import AuditEvaluator


class WDARuntime:
    """
    Walking Data Audit runtime.
    """

    def __init__(self, persist_fn=None):
        self.policy = AuditPolicy()
        self.evaluator = AuditEvaluator()
        self.persist_fn = persist_fn

    def should_audit(self, event) -> bool:
        return self.policy.should_audit(event)

    def run(self, event):
        eat = self.evaluator.evaluate(event)

        if self.persist_fn:
            self.persist_fn(eat)

        return eat
