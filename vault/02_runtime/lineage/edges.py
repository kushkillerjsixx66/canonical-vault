class LineageEdges:
    def build(self, record_type, envelope):
        return {
            "record_type": record_type,
            "target_id": envelope["payload"].get("id"),
            "source_ids": envelope.get("source_artifact_ids", []),
            "timestamp": envelope.get("commit_timestamp")
        }
