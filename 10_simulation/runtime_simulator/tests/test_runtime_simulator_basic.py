from ..simulator import RuntimeSimulator


def test_runtime_simulator_boot_and_scenario():
    sim = RuntimeSimulator(delay=0.0)
    sim.start()
    sim.scenario_basic_runtime()
    sim.stop()
