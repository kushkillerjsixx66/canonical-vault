from ..stumpy_enforcement_pipelines import EnforcementProcess
from multiprocessing import Queue


def test_enforcement_runtime_trigger():
    eq = Queue()
    vq = Queue()
    proc = EnforcementProcess(eq, vq)

    event = {
        "type": "runtime_state",
        "payload": {"unsafe": True},
    }
    proc._route_event(event)

    assert not vq.empty()
    v = vq.get()
    assert v["type"] == "runtime_enforcement_triggered"
