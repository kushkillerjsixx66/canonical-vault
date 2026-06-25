class RecordSchema:
    def validate(self, record_type_schema, payload):
        missing = [k for k in record_type_schema["fields"] if k not in payload]
        if missing:
            raise ValueError(f"Missing fields: {missing}")
