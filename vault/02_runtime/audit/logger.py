import json
from pathlib import Path

class AuditLogger:
    def log(self, event_type, record_type, envelope, record_path):
        audit_dir = record_path.parent / "_audit"
        audit_dir.mkdir(exist_ok=True)
        log_path = audit_dir / "audit.log"
        entry = {
            "event_type": event_type,
            "record_type": record_type,
            "record_path": str(record_path),
            "operator_id": envelope.get("provenance", {}).get("operator_id"),
            "timestamp": envelope.get("commit_timestamp")
        }
        if log_path.exists():
            data = json.loads(log_path.read_text())
        else:
            data = {"events": []}
        data["events"].append(entry)
        log_path.write_text(json.dumps(data, indent=2))
