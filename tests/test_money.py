from decimal import Decimal

from app.money import gain_loss, round_money


def test_tc_calc_01_rounds_half_up_to_two_places():
    assert round_money(Decimal("91666.666")) == Decimal("91666.67")
    assert round_money(Decimal("0.125")) == Decimal("0.13")


def test_tc_calc_01_adding_amounts_has_no_float_error():
    assert Decimal("0.10") + Decimal("0.20") == Decimal("0.30")


def test_tc_calc_01_gain_and_loss():
    assert gain_loss(Decimal("120"), Decimal("100")) == (Decimal("20.00"), Decimal("20.00"))
    assert gain_loss(Decimal("90"), Decimal("100")) == (Decimal("-10.00"), Decimal("-10.00"))
    assert gain_loss(Decimal("50"), Decimal("0")) == (Decimal("50.00"), Decimal("0.00"))
