from decimal import Decimal

import pytest

from scraper.normalizer import (
    calculate_price_per_unit,
    normalize_observation,
    parse_money,
    parse_size,
)


@pytest.mark.parametrize(
    ("raw", "expected"),
    [
        ("$4.99", Decimal("4.99")),
        ("CAD 6.50", Decimal("6.50")),
        (Decimal("7.1"), Decimal("7.10")),
    ],
)
def test_parse_money(raw, expected):
    assert parse_money(raw) == expected


@pytest.mark.parametrize(
    ("raw", "weight_g", "volume_ml"),
    [
        ("500 g", Decimal("500.00"), None),
        ("1 kg", Decimal("1000.00"), None),
        ("2 x 250 g", Decimal("500.00"), None),
        ("1.5 L", None, Decimal("1500.00")),
        ("650 ml", None, Decimal("650.00")),
    ],
)
def test_parse_size(raw, weight_g, volume_ml):
    assert parse_size(raw) == (weight_g, volume_ml)


def test_calculate_price_per_unit_for_weight():
    ppu, unit = calculate_price_per_unit(Decimal("4.99"), weight_g=Decimal("500"))

    assert ppu == Decimal("0.9980")
    assert unit == "100g"


def test_normalize_observation_builds_metric_record():
    observation = normalize_observation(
        name="Maple Crunch Cereal",
        store="Walmart",
        price="$4.99",
        package_size="450 g",
        brand="Northern Pantry",
        category="Pantry",
    )

    assert observation.store == "walmart"
    assert observation.weight_g == Decimal("450.00")
    assert observation.price_per_unit == Decimal("1.1089")
    assert observation.unit_type == "100g"
