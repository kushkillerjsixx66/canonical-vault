# 05_runtime package — Canonical Lattice Runtime
# Added in v1.1 patch: missing __init__.py prevented all package imports.
from importlib.metadata import version, PackageNotFoundError
try:
    __version__ = version("canonical-vault")
except PackageNotFoundError:
    __version__ = "1.1.0-patch"
