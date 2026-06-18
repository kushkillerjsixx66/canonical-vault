"""
conftest.py — Canonical Lattice Test Suite
Location: 05_runtime/tests/conftest.py

Adds the 05_runtime/ directory to sys.path at pytest collection time so that
all test files can import top-level modules (lattice_config, sentinel, veil,
vara, stumpy, vault, etc.) without manual path manipulation or importlib hacks.

Provides shared fixtures used across test_lattice_config.py,
test_invariants.py, and any future test modules.
"""

import sys
import pathlib
import importlib

import pytest

# ---------------------------------------------------------------------------
# Path bootstrap
# ---------------------------------------------------------------------------
# Resolve the 05_runtime/ directory (one level above this conftest.py)
# and prepend it to sys.path so that `import lattice_config` etc. work
# cleanly from any working directory when pytest is invoked.

_RUNTIME_DIR = pathlib.Path(__file__).resolve().parent.parent
if str(_RUNTIME_DIR) not in sys.path:
    sys.path.insert(0, str(_RUNTIME_DIR))

# ---------------------------------------------------------------------------
# pytest rootdir / ini options (inline — no separate pytest.ini needed)
# ---------------------------------------------------------------------------
# Place a pytest.ini or pyproject.toml in 05_runtime/ if you need persistent
# ini options. The block below documents the recommended minimal config:
#
#   [pytest]
#   testpaths = tests
#   python_files = test_*.py
#   python_classes = Test*
#   python_functions = test_*
#   addopts = -v --tb=short
#
# With this conftest.py present, running `pytest` from 05_runtime/ is
# sufficient — no PYTHONPATH export required.


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def cfg():
    """
    Session-scoped LatticeConfig instance.

    Imported lazily so the fixture fails gracefully with a clear error if
    lattice_config.py is not yet on sys.path (misconfigured environment).
    """
    try:
        from lattice_config import LatticeConfig
    except ImportError as exc:
        pytest.fail(
            f"Could not import LatticeConfig from lattice_config.py. "
            f"Ensure conftest.py is in 05_runtime/tests/ and that "
            f"05_runtime/ is the pytest rootdir. Original error: {exc}"
        )
    return LatticeConfig()


@pytest.fixture(scope="session")
def cfg_module():
    """
    Session-scoped reference to the lattice_config module itself.

    Useful for tests that need to inspect module-level constants or
    re-instantiate config objects with custom overrides.
    """
    try:
        import lattice_config
    except ImportError as exc:
        pytest.fail(
            f"Could not import lattice_config module. "
            f"Original error: {exc}"
        )
    return lattice_config


@pytest.fixture(scope="session")
def sentinel_module():
    """
    Session-scoped reference to the sentinel module.

    Returns None (and emits a pytest.skip) if sentinel.py is not importable —
    allowing test_invariants.py sentinel-runtime checks to be skipped cleanly
    on a fresh checkout before dependencies are installed.
    """
    try:
        import sentinel
        return sentinel
    except ImportError:
        return None


@pytest.fixture(scope="session")
def stumpy_module():
    """
    Session-scoped reference to the stumpy module.

    Returns None and skips if stumpy.py is not importable.
    """
    try:
        import stumpy
        return stumpy
    except ImportError:
        return None


@pytest.fixture(scope="session")
def vault_module():
    """
    Session-scoped reference to the vault module.
    """
    try:
        import vault
        return vault
    except ImportError:
        return None


@pytest.fixture(scope="session")
def veil_module():
    """
    Session-scoped reference to the veil module.
    """
    try:
        import veil
        return veil
    except ImportError:
        return None


@pytest.fixture(scope="session")
def vara_module():
    """
    Session-scoped reference to the vara module.
    """
    try:
        import vara
        return vara
    except ImportError:
        return None


# ---------------------------------------------------------------------------
# Helpers exposed as fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def runtime_dir():
    """
    Absolute Path to the 05_runtime/ directory.
    Useful for tests that need to load fixture files or check file presence.
    """
    return _RUNTIME_DIR


@pytest.fixture(scope="session")
def tests_dir():
    """
    Absolute Path to the 05_runtime/tests/ directory.
    """
    return pathlib.Path(__file__).resolve().parent


# ---------------------------------------------------------------------------
# Invariant constants (mirrors lattice_config defaults; used in assertions)
# ---------------------------------------------------------------------------

INVARIANT_CODES = ["I\u00b7COH", "II\u00b7REV", "III\u00b7ATT", "IV\u00b7SIL", "V\u00b7DEC", "VI\u00b7SIG"]

HARD_FAILURE_INVARIANTS = {"I\u00b7COH", "II\u00b7REV", "IV\u00b7SIL"}
SOFT_FAILURE_INVARIANTS  = {"III\u00b7ATT", "V\u00b7DEC", "VI\u00b7SIG"}

GATE_INVARIANT_MAP = {
    "G1": "I\u00b7COH",
    "G2": "III\u00b7ATT",
    "G3": "II\u00b7REV",
}


@pytest.fixture(scope="session")
def invariant_codes():
    """All six canonical invariant mnemonic codes."""
    return list(INVARIANT_CODES)


@pytest.fixture(scope="session")
def hard_failure_invariants():
    """Set of invariants that trigger Hard Failure on violation."""
    return set(HARD_FAILURE_INVARIANTS)


@pytest.fixture(scope="session")
def soft_failure_invariants():
    """Set of invariants that trigger Soft Failure on violation."""
    return set(SOFT_FAILURE_INVARIANTS)


@pytest.fixture(scope="session")
def gate_invariant_map():
    """Mapping of governance gate codes to their bound invariant."""
    return dict(GATE_INVARIANT_MAP)
