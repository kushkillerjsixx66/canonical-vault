import json

class LineageIndex:
    def update(self, edge, index_path):
        if index_path.exists():
            data = json.loads(index_path.read_text())
        else:
            data = {"edges": []}
        data["edges"].append(edge)
        index_path.write_text(json.dumps(data, indent=2))
