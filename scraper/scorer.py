from decimal import Decimal


def severity_from_ppu_change(ppu_change_pct: Decimal) -> str:
    if ppu_change_pct >= Decimal("25"):
        return "critical"
    if ppu_change_pct >= Decimal("15"):
        return "high"
    if ppu_change_pct >= Decimal("8"):
        return "moderate"
    return "low"


def shrink_score(ppu_change_pct: Decimal, weight_drop_pct: Decimal) -> int:
    weighted = (ppu_change_pct * Decimal("0.7")) + (weight_drop_pct * Decimal("0.3"))
    return min(100, max(0, int(weighted.quantize(Decimal("1")))))
