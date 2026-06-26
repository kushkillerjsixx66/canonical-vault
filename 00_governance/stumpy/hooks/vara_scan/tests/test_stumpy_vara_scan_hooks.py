from multiprocessing import Queue
from vault_pipeline.vault_chain.vault_chain import VaultChain
from ..stumpy_vara_scan_hooks import StumpyVaraScanHooks


def test_lineage_corruption_detection(tmp_path):
    chain = VaultChain(root=tmp_path)
    vq = Queue()
    hooks = StumpyVaraScanHooks(chain, vq)

    # Corrupted lineage (missing altitude)
    lineage = [{"seq": 1, "operator_id": "op", "role": "root"}]

    event = {
        "type": "vault_promotion",
        "payload": {"lineage": lineage, "path": "dummy"},
    }

    hooks.handle_vault_promotion(event)

    assert not vq.empty()
    violation = vq.get()
    assert violation["payload"]["violation"] == "lineage_corruption"
