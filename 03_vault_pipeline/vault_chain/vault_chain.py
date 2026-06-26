import json
from pathlib import Path
from typing import Any, List


class VaultChain:
    """
    Canonical Vault Chain.

    Responsibilities:
    - Persist lineage entries
    - Retrieve lineage by seq
    - Verify lineage continuity
    """

    def __init__(self, root: str = "vault/chain") -> None:
        self._root = Path(root)
        self._root.mkdir(parents=True, exist_ok=True)

    # ---- Persistence ---------------------------------------------------

    def append(self, entry: dict[str, Any]) -> Path:
        """
        Append a lineage entry to the chain.

        Uses seq as filename.
        """
        seq = entry["seq"]
        path = self._root / f"lineage_{seq}.json"
        with path.open("w") as f:
            json.dump(entry, f, indent=2)
        return path

    def load(self, seq: int) -> dict[str, Any] | None:
        """
        Load a lineage entry by seq.
        """
        path = self._root / f"lineage_{seq}.json"
        if not path.exists():
            return None
        with path.open() as f:
            return json.load(f)

    def load_all(self) -> List[dict[str, Any]]:
        """
        Load all lineage entries in order.
        """
        entries: List[dict[str, Any]] = []
        for path in sorted(self._root.glob("lineage_*.json")):
            with path.open() as f:
                entries.append(json.load(f))
        return entries

    # ---- Verification --------------------------------------------------

    def verify_continuity(self) -> bool:
        """
        Verify that seq values are continuous and start at 1.
        """
        entries = self.load_all()
        if not entries:
            return True

        seqs = sorted(e["seq"] for e in entries)
        expected = list(range(1, len(seqs) + 1))
        return seqs == expected

    def verify_entry(self, entry: dict[str, Any]) -> bool:
        """
        Verify a single lineage entry has required fields.
        """
        required = ("seq", "operator_id", "role", "altitude")
        return all(k in entry for k in required)
