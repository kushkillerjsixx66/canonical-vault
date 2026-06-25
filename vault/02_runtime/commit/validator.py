class CommitValidator:
    def validate(self, envelope, pattern, record_schema):
        missing = [f for f in pattern["commit_envelope"]["required_fields"] if f not in envelope]
        if missing:
            raise ValueError(f"Missing commit envelope fields: {missing}")
        return envelope
