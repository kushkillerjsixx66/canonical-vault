"""
Vara – Epistemic Supervisor

Canonical implementation:
- Handles Veil runtime state.
- Builds epistemic context (identity + runtime + lineage).
- Emits epistemic_state events to Stumpy.
"""

from .vara_core import Vara
from .vara_interface import VaraInterface

__all__ = ["Vara", "VaraInterface"]
