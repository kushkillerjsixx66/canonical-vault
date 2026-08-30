"""
run_lattice.py — Top-level launch script
PATCH v1.1: FIX import path from 'runtime.adapter.canonical_adapter'
(wrong AND missing) to 'adapter.canonical_adapter' (correct relative path).
"""
from __future__ import annotations
import sys, os
_DIR = os.path.dirname(os.path.abspath(__file__))
if _DIR not in sys.path: sys.path.insert(0, _DIR)

try:
    from adapter.canonical_adapter import CanonicalAdapter   # FIX
    _ADAPTER_OK = True
except ImportError as _e:
    _ADAPTER_OK = False; _ADAPTER_ERR = str(_e)

from lattice_runtime import LatticeREPL

def main() -> None:
    if not _ADAPTER_OK:
        print(f"[WARNING] CanonicalAdapter unavailable: {_ADAPTER_ERR}\n"
              "          Continuing without adapter.")
    repl = LatticeREPL()
    if _ADAPTER_OK:
        repl.lattice._adapter = CanonicalAdapter(repl.lattice)
    repl.run()

if __name__ == "__main__":
    main()
