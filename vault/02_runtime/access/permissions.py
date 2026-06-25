class Permissions:
    def load(self, path):
        import json
        return json.loads(path.read_text())
