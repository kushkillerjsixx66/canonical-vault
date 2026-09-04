"""
Legacy Lattice Core - Containment Lockout
=========================================
Status: DEPRECATED / NON-AUTHORITATIVE / LOCKED
"""

from .governance.contracts import NonAuthoritativeRuntimeError


class Lattice:
    def __init__(self, *args, **kwargs):
        raise NonAuthoritativeRuntimeError(
            "Legacy lattice_core.Lattice is deprecated and non-authoritative. "
            "All runtime execution must be routed through the authoritative GovernanceBoundary."
        )
