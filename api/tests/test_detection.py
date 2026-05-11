from decimal import Decimal

from scraper.detector import SnapshotRecord, detect_shrink_event
from scraper.scorer import severity_from_ppu_change, shrink_score


def test_detects_weight_drop_with_same_price(baseline_snapshot):
    current = SnapshotRecord(
        product_id="cereal-001",
        store="walmart",
        price=Decimal("4.99"),
        weight_g=Decimal("450"),
        price_per_unit=Decimal("1.1089"),
    )

    event = detect_shrink_event(baseline_snapshot, current)

    assert event is not None
    assert event.weight_drop_pct == Decimal("10.00")
    assert event.ppu_change_pct == Decimal("11.11")
    assert event.severity == "moderate"


def test_ignores_small_package_size_changes(baseline_snapshot):
    current = SnapshotRecord(
        product_id="cereal-001",
        store="walmart",
        price=Decimal("4.99"),
        weight_g=Decimal("490"),
        price_per_unit=Decimal("1.0184"),
    )

    assert detect_shrink_event(baseline_snapshot, current) is None


def test_ignores_real_discount_even_when_weight_drops(baseline_snapshot):
    current = SnapshotRecord(
        product_id="cereal-001",
        store="walmart",
        price=Decimal("4.49"),
        weight_g=Decimal("450"),
        price_per_unit=Decimal("0.9978"),
    )

    assert detect_shrink_event(baseline_snapshot, current) is None


def test_ignores_different_store_or_product(baseline_snapshot):
    current = SnapshotRecord(
        product_id="cereal-001",
        store="loblaws",
        price=Decimal("4.99"),
        weight_g=Decimal("450"),
        price_per_unit=Decimal("1.1089"),
    )

    assert detect_shrink_event(baseline_snapshot, current) is None


def test_severity_and_score_boundaries():
    assert severity_from_ppu_change(Decimal("4.99")) == "low"
    assert severity_from_ppu_change(Decimal("8.00")) == "moderate"
    assert severity_from_ppu_change(Decimal("15.00")) == "high"
    assert severity_from_ppu_change(Decimal("25.00")) == "critical"
    assert shrink_score(Decimal("20"), Decimal("10")) == 17
