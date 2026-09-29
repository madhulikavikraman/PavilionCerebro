from cascade.gate import route
from cascade.schema import GateOutput


def test_unusable_always_routes():
    assert route(GateOutput(usable=False, damage_present=False, confidence=0.99, reason="blur"))


def test_damage_routes():
    assert route(GateOutput(usable=True, damage_present=True, confidence=0.3, reason="crack"))


def test_confident_no_damage_skips():
    assert not route(GateOutput(usable=True, damage_present=False, confidence=0.9, reason="clean"))


def test_low_confidence_no_damage_routes():
    assert route(GateOutput(usable=True, damage_present=False, confidence=0.5, reason="unsure"))
