class CommitEnvelope:
    def build(self, record_type, payload, metadata):
        return {
            "record_type": record_type,
            "payload": payload,
            **metadata
        }
