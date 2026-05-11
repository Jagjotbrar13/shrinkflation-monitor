from decimal import Decimal

import pytest

from scraper.detector import SnapshotRecord


@pytest.fixture
def baseline_snapshot() -> SnapshotRecord:
    return SnapshotRecord(
        product_id="cereal-001",
        store="walmart",
        price=Decimal("4.99"),
        weight_g=Decimal("500"),
        price_per_unit=Decimal("0.9980"),
        unit_type="100g",
    )
