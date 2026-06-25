class LineageAnchors:
    def extract(self, envelope):
        return envelope.get("lineage_anchors", [])
