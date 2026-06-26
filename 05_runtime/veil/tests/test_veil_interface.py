from multiprocessing import Queue
from ..veil_interface import VeilInterface
from ...vara.vara_interface import VaraInterface


def test_veil_forwards_to_vara():
    eq = Queue()
    vara = VaraInterface(eq)
    veil = VeilInterface(eq, vara)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
    raw_state = {"altitude": "runtime"}

    veil.submit_runtime_update(identity, raw_state)

    # First event is runtime_state from Veil
    event1 = eq.get()
    assert event1["type"] == "runtime_state"

    # Second event is epistemic_state from Vara
    event2 = eq.get()
    assert event2["type"] == "epistemic_state"
    assert event2["source"] == "vara"
