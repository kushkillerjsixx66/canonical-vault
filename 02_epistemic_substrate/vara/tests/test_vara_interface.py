from multiprocessing import Queue
from ..vara_interface import VaraInterface


def test_vara_emits_canonical_epistemic_state():
    eq = Queue()
    vara = VaraInterface(eq)

    identity = {"operator_id": "op1", "role": "root", "sovereignty": "root"}
    runtime = {"altitude": "runtime"}

    vara.handle_veil_state(identity, runtime)

    assert not eq.empty()
    event = eq.get()

    assert event["type"] == "epistemic_state"
    assert event["source"] == "vara"

    payload = event["payload"]
    assert payload["identity"]["operator_id"] == "op1"
    assert payload["runtime"]["altitude"] == "runtime"

    lineage = payload["lineage"]
    assert isinstance(lineage, list)
    assert lineage[0]["seq"] == 1
    assert lineage[0]["operator_id"] == "op1"
    assert lineage[0]["altitude"] == "runtime"
