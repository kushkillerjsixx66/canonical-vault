from multiprocessing import Queue
from ..operator_commands import OperatorCommands


def test_operator_runtime_command():
    class Dummy:
        def submit_runtime_update(self, identity, state):
            self.called = True

    veil = Dummy()
    cmds = OperatorCommands(veil, None, None, None, None, None)

    cmds.execute("runtime", {"operator_id": "op"}, {"altitude": "runtime"}, None, None)
    assert veil.called
