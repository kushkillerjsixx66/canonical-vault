from ..vara_lineage import LineageTracker


def test_lineage_tracker_canonical():
    tracker = LineageTracker()
    identity = {"operator_id": "op1", "role": "root"}
    runtime = {"altitude": "runtime"}

    lineage = tracker.extend(identity, runtime)
    assert isinstance(lineage, list)
    assert len(lineage) == 1

    entry = lineage[0]
    assert entry["seq"] == 1
    assert entry["operator_id"] == "op1"
    assert entry["role"] == "root"
    assert entry["altitude"] == "runtime"
