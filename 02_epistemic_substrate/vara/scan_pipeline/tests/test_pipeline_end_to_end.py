from multiprocessing import Queue
from vara.scan_pipeline.vara_scan_pipeline import VaraScanPipeline


def test_pipeline_end_to_end(tmp_path, monkeypatch):
    eq = Queue()

    # Redirect Vault store to tmp_path
    monkeypatch.setattr(
        "vault_pipeline.vara_scan_integration.vault_scan_store.VaultScanStore._root",
        tmp_path
    )

    pipeline = VaraScanPipeline(eq)

    artifact = {"text": "x" * 200}
    lineage = [{"seq": 1, "operator_id": "op", "role": "root", "altitude": "runtime"}]
    runtime_state = {"altitude": "runtime", "posture": "focused"}

    result = pipeline.run(artifact, lineage, runtime_state)

    assert result is not None
    assert len(result.weak_signals) == 1

    # Promotion event should be emitted
    event = eq.get()
    assert event["type"] in ("vault_promotion", "epistemic_violation")
