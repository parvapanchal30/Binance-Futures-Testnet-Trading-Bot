from typing import Optional


class ValidationError(ValueError):
    pass


def validate_symbol(symbol: str) -> str:
    if not symbol or not symbol.isalnum():
        raise ValidationError("symbol must be alphanumeric, e.g. BTCUSDT")
    return symbol.upper()


def validate_side(side: str) -> str:
    s = side.upper()
    if s not in {"BUY", "SELL"}:
        raise ValidationError("side must be BUY or SELL")
    return s


def validate_order_type(order_type: str) -> str:
    t = order_type.upper()
    if t not in {"MARKET", "LIMIT"}:
        raise ValidationError("order type must be MARKET or LIMIT")
    return t


def validate_quantity(quantity: str | float | int) -> float:
    try:
        q = float(quantity)
    except Exception:
        raise ValidationError("quantity must be a number")
    if q <= 0:
        raise ValidationError("quantity must be > 0")
    return q


def validate_price(price: Optional[str | float | int], order_type: str) -> Optional[float]:
    if order_type.upper() == "LIMIT":
        if price is None:
            raise ValidationError("price is required for LIMIT orders")
        try:
            p = float(price)
        except Exception:
            raise ValidationError("price must be a number")
        if p <= 0:
            raise ValidationError("price must be > 0")
        return p
    return None


__all__ = [
    "ValidationError",
    "validate_symbol",
    "validate_side",
    "validate_order_type",
    "validate_quantity",
    "validate_price",
]
