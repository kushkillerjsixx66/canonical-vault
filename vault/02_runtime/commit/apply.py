import json
from pathlib import Path

class CommitApply:
    def apply(self, record_type, envelope, paths):
        record_id = envelope["payload"].get(f"{record_type.split('_')[0]}_id")
        record_dir = paths.records / record_type
        record_dir.mkdir(parents=True, exist_ok=True)
        path = record_dir / f"{record_id}.json"
        path.write_text(json.dumps(envelope, indent=2))
        return path
