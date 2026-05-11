import re
from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal, InvalidOperation

MONEY_PATTERN = re.compile(r"(?P<amount>\d+(?:[.,]\d{1,2})?)")
SIZE_PATTERN = re.compile(
    r"(?:(?P<count>\d+)\s*[xX]\s*)?(?P<amount>\d+(?:[.,]\d+)?)\s*(?P<unit>kg|g|mg|l|L|ml|mL)\b"
)


@dataclass(frozen=True)
class ProductObservation:
    name: str
    store: str
    price: Decimal
    location: str = "edmonton"
    barcode: str | None = None
    brand: str | None = None
    category: str | None = None
    subcategory: str | None = None
    weight_g: Decimal | None = None
    volume_ml: Decimal | None = None
    price_per_unit: Decimal | None = None
    unit_type: str | None = None


def quantize(value: Decimal, places: str = "0.01") -> Decimal:
    return value.quantize(Decimal(places), rounding=ROUND_HALF_UP)


def parse_money(raw_price: str | Decimal | float | int) -> Decimal:
    if isinstance(raw_price, Decimal):
        return quantize(raw_price)
    if isinstance(raw_price, int | float):
        return quantize(Decimal(str(raw_price)))

    match = MONEY_PATTERN.search(raw_price.replace(",", "."))
    if not match:
        raise ValueError(f"Could not parse price from {raw_price!r}")
    return quantize(Decimal(match.group("amount")))


def parse_size(raw_size: str) -> tuple[Decimal | None, Decimal | None]:
    matches = list(SIZE_PATTERN.finditer(raw_size))
    if not matches:
        return None, None

    total_weight_g = Decimal("0")
    total_volume_ml = Decimal("0")
    for match in matches:
        count = Decimal(match.group("count") or "1")
        amount = Decimal(match.group("amount").replace(",", "."))
        unit = match.group("unit").lower()

        if unit == "kg":
            total_weight_g += count * amount * Decimal("1000")
        elif unit == "g":
            total_weight_g += count * amount
        elif unit == "mg":
            total_weight_g += count * amount / Decimal("1000")
        elif unit == "l":
            total_volume_ml += count * amount * Decimal("1000")
        elif unit == "ml":
            total_volume_ml += count * amount

    weight = quantize(total_weight_g) if total_weight_g > 0 else None
    volume = quantize(total_volume_ml) if total_volume_ml > 0 else None
    return weight, volume


def calculate_price_per_unit(
    price: Decimal,
    weight_g: Decimal | None = None,
    volume_ml: Decimal | None = None,
) -> tuple[Decimal | None, str | None]:
    try:
        if weight_g and weight_g > 0:
            return quantize((price / weight_g) * Decimal("100"), "0.0001"), "100g"
        if volume_ml and volume_ml > 0:
            return quantize((price / volume_ml) * Decimal("100"), "0.0001"), "100ml"
    except (InvalidOperation, ZeroDivisionError):
        return None, None
    return None, None


def normalize_observation(
    *,
    name: str,
    store: str,
    price: str | Decimal | float | int,
    package_size: str,
    location: str = "edmonton",
    barcode: str | None = None,
    brand: str | None = None,
    category: str | None = None,
    subcategory: str | None = None,
) -> ProductObservation:
    normalized_price = parse_money(price)
    weight_g, volume_ml = parse_size(package_size)
    price_per_unit, unit_type = calculate_price_per_unit(normalized_price, weight_g, volume_ml)

    return ProductObservation(
        barcode=barcode,
        name=name.strip(),
        brand=brand.strip() if brand else None,
        category=category,
        subcategory=subcategory,
        store=store.lower().strip(),
        location=location.lower().strip(),
        price=normalized_price,
        weight_g=weight_g,
        volume_ml=volume_ml,
        price_per_unit=price_per_unit,
        unit_type=unit_type,
    )
