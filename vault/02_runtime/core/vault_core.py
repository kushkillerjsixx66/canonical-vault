class VaultCore:
    """
    Canonical Vault core API.
    Handles commit, read, lock, archive, delete.
    All operations must pass through this layer.
    """
    def __init__(self, state, paths, commit_handler, record_loader,
                 rbac, retention, lineage, governance, audit):
        self.state = state
        self.paths = paths
        self.commit_handler = commit_handler
        self.record_loader = record_loader
        self.rbac = rbac
        self.retention = retention
        self.lineage = lineage
        self.governance = governance
        self.audit = audit

    def commit(self, operator_role, record_type, payload, metadata):
        self.rbac.check(operator_role, "commit", record_type)
        envelope = self.commit_handler.validate_envelope(record_type, payload, metadata)
        self.retention.assign(record_type, envelope)
        record_path = self.commit_handler.apply(record_type, envelope)
        self.lineage.register(record_type, envelope)
        self.governance.on_commit(record_type, envelope)
        self.audit.log("commit", record_type, envelope, record_path)
        return record_path
