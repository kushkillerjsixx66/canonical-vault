import json
from pathlib import Path

class RecordLoader:
    def load(self, record_type, record_id, paths):
        path = paths.records / record_type / f"{record_id}.json"
        return json.loads(path.read_text())
