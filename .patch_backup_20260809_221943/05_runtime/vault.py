import json

class Vault:

    def __init__(self):
        self.records = []

    def store(self, data):
        self.records.append(data)

    def export(self, path="vault.json"):
        with open(path, "w") as f:
            json.dump(self.records, f, indent=2)