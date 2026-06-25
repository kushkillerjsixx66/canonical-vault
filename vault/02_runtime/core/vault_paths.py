from pathlib import Path

class VaultPaths:
    def __init__(self, root):
        self.root = Path(root)
        self.records = self.root / "04_records"
        self.lineage = self.root / "05_lineage"
        self.governance = self.root / "06_governance"
