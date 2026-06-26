from multiprocessing import Queue
from ..field_intel_scheduler import FieldIntelScheduler


def test_field_intel_scheduler(tmp_path, monkeypatch):
    eq = Queue()

    # Redirect Vault root
    monkeypatch.setattr(
        "07_content_engine.field_intel_friday.field_intel_scheduler.FieldIntelScheduler._vault_root",
        tmp_path
    )

    scheduler = FieldIntelScheduler(eq, vault_root=tmp_path)

    artifacts = [{"text": "x" * 200}]
    runtime_state = {"altitude": "runtime", "posture": "focused"}

    path = scheduler.run(artifacts, runtime_state)

    assert path.endswith(".txt")
