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

    # multiprocessing.Queue.empty() is inherently racy immediately after put().
    violation = vq.get(timeout=1)
    assert violation["payload"]["violation"] == "lineage_corruption"
