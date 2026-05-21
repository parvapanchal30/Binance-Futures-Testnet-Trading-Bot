from typing import Optional
from .client import BinanceFuturesClient, BinanceAPIError
from .logging_config import setup_logging

logger = setup_logging()


def place_and_report(
    client: BinanceFuturesClient,
    symbol: str,
    side: str,
    order_type: str,
    quantity: float,
    price: Optional[float] = None,
):
    """Place an order and return a concise report dict."""
    try:
        resp = client.place_order(symbol, side, order_type, quantity, price)
    except BinanceAPIError as e:
        logger.error("Order failed: %s", e)
        return {"success": False, "error": str(e)}

    # Extract commonly useful fields
    report = {
        "success": True,
        "orderId": resp.get("orderId"),
        "status": resp.get("status"),
        "executedQty": resp.get("executedQty") or resp.get("executedQty", "0"),
        "avgPrice": resp.get("avgPrice") or resp.get("avgPrice", None),
        "raw": resp,
    }

    logger.info("Order placed successfully: %s", report)
    return report


__all__ = ["place_and_report"]
