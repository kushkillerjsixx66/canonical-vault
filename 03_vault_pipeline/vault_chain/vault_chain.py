import json
from pathlib import Path
from typing import Any, List


class VaultChain:
    """Canonical Vault Chain with immutable sequence records."""

    def __init__(self, root: str = "vault/chain") -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    def append(self, entry: dict[str, Any]) -> Path:
        """Append a lineage entry without overwriting an existing sequence."""
        seq = entry["seq"]
        path = self._root / f"lineage_{seq}.json"
        if path.exists():
            raise FileExistsError(f"lineage sequence {seq} already exists")
        with path.open("x") as f:
            json.dump(entry, f, indent=2)
        return path

    def load(self, seq: int) -> dict[str, Any] | None:
        path = self._root / f"lineage_{seq}.json"
        if not path.exists():
            return None
        with path.open() as f:
            return json.load(f)

    def load_all(self) -> List[dict[str, Any]]:
        entries: List[dict[str, Any]] = []
        for path in sorted(self._root.glob("lineage_*.json")):
            with path.open() as f:
                entries.append(json.load(f))
        return entries

    def verify_continuity(self) -> bool:
        entries = self.load_all()
        if not entries:
            return True
        seqs = sorted(e["seq"] for e in entries)
        return seqs == list(range(1, len(seqs) + 1))

    def verify_entry(self, entry: dict[str, Any]) -> bool:
        required = ("seq", "operator_id", "role", "altitude")
        return all(k in entry for k in required)
