from .types import Mechanism


class MechanismSelector:
    """
    Selects a mechanism based on intent text and PAM verdict.
    """

    def select(self, intent_text: str, pam_verdict: str) -> Mechanism:
        lower = intent_text.lower()

        if "summarize" in lower:
            mech = "summarization"
        elif "classify" in lower:
            mech = "classification"
        elif "analyze" in lower:
            mech = "analysis"
        else:
            mech = "generation"

        if pam_verdict != "CLEAR":
            mech = f"safe_{mech}"

        return Mechanism(
            name=mech,
            description=f"Mechanism selected for intent '{intent_text}' with PAM verdict '{pam_verdict}'."
        )
