"""
conftest.py — Canonical Lattice, repository root
==================================================
Authority: repo root (applies to every test under this tree)

Purpose
-------
Several test modules (chiefly `tests/integration/*` and a handful of
cross-subsystem tests under `02_epistemic_substrate/` and
`00_governance/`) import top-level dotted names that describe the
*conceptual* layer they belong to rather than the literal on-disk
directory name, e.g.:

    from governance.stumpy.stumpy_engine import StumpyEngine
    from epistemic.vara.vara_interface import VaraInterface
    from runtime.veil.veil_interface import VeilInterface
    from vault_pipeline.vault_chain.vault_chain import VaultChain

The actual directories are numeric-prefixed (`00_governance/`,
`02_epistemic_substrate/`, `05_runtime/`, `03_vault_pipeline/`) and
cannot be imported under those names — a leading digit is not a
legal Python identifier.

Rather than renaming ten top-level directories (a large, high-risk
diff touching every doc and manifest that references them by path),
this registers lightweight namespace-package aliases: synthetic
modules whose `__path__` points at the real numeric directory. This
is the standard technique for exposing an existing directory tree
under an alternate import name and requires no files to move.

Most other test failures across the suite were caused by missing
`__init__.py` files breaking the relative-import package chain
(`from ..module import X`) — those have been restored directly on
disk rather than patched here, since that's the real bug, not an
aliasing problem.
"""

import sys
import types
import pathlib

_ROOT = pathlib.Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# 1. sys.path insertion for every numeric-prefixed top-level directory.
#
# This generalizes the pattern already used by 05_runtime/tests/conftest.py
# (which inserts 05_runtime/ so that lattice_config, sentinel, vault, veil,
# vara, stumpy, etc. import as flat top-level names) to every subsystem
# directory, so e.g. `import stumpy` resolves regardless of which test
# happens to run first in a given pytest session.
# ---------------------------------------------------------------------------
for _entry in sorted(_ROOT.iterdir()):
    if _entry.is_dir() and _entry.name[:2].isdigit() and _entry.name[2:3] == "_":
        _p = str(_entry)
        if _p not in sys.path:
            sys.path.insert(0, _p)

# ---------------------------------------------------------------------------
# 2. Alias imports for cross-subsystem names that don't match any real
# on-disk directory name directly (the numeric prefix stops them being
# importable under their own name; "boot" additionally expects a wrapper
# level that doesn't exist on disk — 09_boot/lattice_boot/... is imported
# as `boot.lattice_boot...`).
# ---------------------------------------------------------------------------
_ALIASES = {
    "governance": "00_governance",
    "epistemic": "02_epistemic_substrate",
    "vault_pipeline": "03_vault_pipeline",
    "runtime": "05_runtime",
    "boot": "09_boot",
    "content_engine": "07_content_engine",
}

for _alias, _real_dirname in _ALIASES.items():
    if _alias in sys.modules:
        continue
    _real_path = _ROOT / _real_dirname
    if not _real_path.is_dir():
        continue
    _pkg = types.ModuleType(_alias)
    _pkg.__path__ = [str(_real_path)]
    _pkg.__is_lattice_alias__ = True  # marker, harmless if inspected
    sys.modules[_alias] = _pkg
