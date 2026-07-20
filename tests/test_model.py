import pytest

from fmea_tool import FailureMode, FMEAAnalysis


def _make(severity: int, occurrence: int, detection: int, name: str = "x") -> FailureMode:
    return FailureMode(
        component=name, function="f", failure_mode=name, effect="e",
        severity=severity, occurrence=occurrence, detection=detection,
    )


def test_rpn_is_the_product_of_the_three_ratings():
    fm = _make(severity=7, occurrence=4, detection=5)
    assert fm.rpn == 140


def test_risk_level_bands():
    assert _make(10, 10, 10).risk_level == "CRITICAL"  # RPN 1000
    assert _make(5, 5, 5).risk_level == "HIGH"          # RPN 125
    assert _make(4, 3, 4).risk_level == "MEDIUM"        # RPN 48
    assert _make(2, 2, 2).risk_level == "LOW"           # RPN 8


@pytest.mark.parametrize("bad_value", [0, 11, -1])
def test_out_of_range_ratings_are_rejected(bad_value):
    with pytest.raises(ValueError):
        _make(severity=bad_value, occurrence=5, detection=5)


def test_ranked_sorts_highest_risk_first():
    analysis = FMEAAnalysis(title="t")
    low = _make(2, 2, 2, "low")
    high = _make(9, 8, 7, "high")
    mid = _make(5, 5, 4, "mid")
    for fm in [low, high, mid]:
        analysis.add(fm)

    ranked = analysis.ranked()
    assert [fm.component for fm in ranked] == ["high", "mid", "low"]


def test_above_threshold_filters_correctly():
    analysis = FMEAAnalysis(title="t")
    analysis.add(_make(9, 8, 7, "critical"))  # RPN 504
    analysis.add(_make(2, 2, 2, "negligible"))  # RPN 8

    above = analysis.above_threshold(rpn_threshold=100)
    assert len(above) == 1
    assert above[0].component == "critical"
