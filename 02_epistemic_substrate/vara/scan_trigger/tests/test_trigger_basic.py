from vara.scan.vara_scan_schema import VaraScanResult
from ..vara_scan_trigger import VaraScanTrigger


def test_trigger_runs_scan():
    trigger = VaraScanTrigger()

    artifact = {"text": "x" * 200}
    lineage = [{"seq": 1, "operator_id": "op", "role": "root", "altitude": "runtime"}]
    runtime_state = {"altitude": "runtime", "posture": "focused"}

    result = trigger.maybe_scan(artifact, lineage, runtime_state)

    assert isinstance(result, VaraScanResult)
    assert len(result.weak_signals) == 1
