from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal

from scraper.scorer import severity_from_ppu_change


@dataclass(frozen=True)
class SnapshotRecord:
    product_id: str
    store: str
    price: Decimal
    weight_g: Decimal | None
    price_per_unit: Decimal | None
    unit_type: str | None = "100g"


@dataclass(frozen=True)
class ShrinkEventCandidate:
    product_id: str
    store: str
    old_weight_g: Decimal
    new_weight_g: Decimal
    old_price: Decimal
    new_price: Decimal
    old_ppu: Decimal
    new_ppu: Decimal
    weight_drop_pct: Decimal
    ppu_change_pct: Decimal
    severity: str


def pct_change(old: Decimal, new: Decimal) -> Decimal:
    if old <= 0:
        return Decimal("0.00")
    return ((new - old) / old * Decimal("100")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def detect_shrink_event(
    previous: SnapshotRecord,
    current: SnapshotRecord,
    *,
    min_weight_drop_pct: Decimal = Decimal("3.00"),
    price_tolerance_pct: Decimal = Decimal("1.00"),
) -> ShrinkEventCandidate | None:
    if previous.product_id != current.product_id or previous.store != current.store:
        return None
    if not previous.weight_g or not current.weight_g:
        return None
    if not previous.price_per_unit or not current.price_per_unit:
        return None
    if current.weight_g >= previous.weight_g:
        return None

    weight_drop_pct = (
        (previous.weight_g - current.weight_g) / previous.weight_g * Decimal("100")
    ).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    if weight_drop_pct < min_weight_drop_pct:
        return None

    price_change_pct = pct_change(previous.price, current.price)
    if price_change_pct < -price_tolerance_pct:
        return None

    ppu_change_pct = pct_change(previous.price_per_unit, current.price_per_unit)
    if ppu_change_pct <= 0:
        return None

    return ShrinkEventCandidate(
        product_id=current.product_id,
        store=current.store,
        old_weight_g=previous.weight_g,
        new_weight_g=current.weight_g,
        old_price=previous.price,
        new_price=current.price,
        old_ppu=previous.price_per_unit,
        new_ppu=current.price_per_unit,
        weight_drop_pct=weight_drop_pct,
        ppu_change_pct=ppu_change_pct,
        severity=severity_from_ppu_change(ppu_change_pct),
    )
