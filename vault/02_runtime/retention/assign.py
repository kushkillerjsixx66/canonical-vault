class RetentionAssign:
    def assign(self, record_type, envelope, policies):
        cls = policies["assignment_rules"].get(record_type)
        if not cls:
            raise ValueError(f"No retention class for {record_type}")
        envelope["retention_class"] = cls
