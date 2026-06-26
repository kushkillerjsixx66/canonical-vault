from ..boot_sequence import LatticeBoot


def test_boot_sequence_start_and_stop():
    boot = LatticeBoot()
    components = boot.start()

    assert "stumpy" in components
    assert "veil" in components
    assert "vara" in components
    assert "scan_pipeline" in components
    assert "chain" in components
    assert "scheduler" in components

    boot.stop()
