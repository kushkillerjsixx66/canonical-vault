from ..vara_scan import VaraScan


def test_basic_scan():
    scan = VaraScan()
    artifact = {"text": "x" * 200, "empty": ""}
    lineage = [{"seq": 1}]

    result = scan.scan(artifact, lineage)

    assert len(result.weak_signals) == 1
    assert "empty" in result.unspecified
    assert result.lineage[0]["seq"] == 1
