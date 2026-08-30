from multiprocessing import Queue
from ..stumpy_drift_detector import DriftDetectorProcess


def test_drift_detector_altitude_violation():
    eq = Queue()
    vq = Queue()
    detector = DriftDetectorProcess(eq, vq)

    event = {
        "type": "runtime_state",
        "source": "veil",
        "payload": {"altitude": "nonsense"},
    }
    detector._inspect_event(event)

    v = vq.get(timeout=1.0)
    assert v["type"] == "altitude_drift"
