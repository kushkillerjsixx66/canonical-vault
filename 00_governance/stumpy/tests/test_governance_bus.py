from multiprocessing import Queue
from ..stumpy_governance_bus import GovernanceBus


def test_governance_bus_unhandled_event():
    eq = Queue()
    vq = Queue()
    bus = GovernanceBus(eq, vq)

    bus.start()
    eq.put({"type": "unknown", "payload": {}})

    import time
    time.sleep(0.5)
    bus.stop()

    assert not vq.empty()
    v = vq.get()
    assert v["type"] == "unhandled_event"
