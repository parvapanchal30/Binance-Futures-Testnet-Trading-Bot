import time
import hmac
import hashlib
from typing import Optional, Dict, Any
import requests
from urllib.parse import urlencode
from .logging_config import setup_logging


logger = setup_logging()


class BinanceAPIError(Exception):
    pass


class BinanceFuturesClient:
    """Minimal Binance USDT-M Futures Testnet client for order placement."""

    def __init__(self, api_key: str, api_secret: str, base_url: str | None = None):
        self.api_key = api_key
        self.api_secret = api_secret
        # Official testnet base for USD-M futures
        self.base_url = base_url 
        self.session = requests.Session()
        self.session.headers.update({"X-MBX-APIKEY": self.api_key})

    def _sign(self, params: Dict[str, Any]) -> str:
        query = urlencode(params)
        signature = hmac.new(
            self.api_secret.encode("utf-8"), query.encode("utf-8"), hashlib.sha256
        ).hexdigest()
        return signature

    def place_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        recv_window: int = 5000,
    ) -> Dict[str, Any]:
        path = "/fapi/v1/order"
        url = f"{self.base_url}{path}"

        params: Dict[str, Any] = {
            "symbol": symbol,
            "side": side,
            "type": order_type,
            "quantity": quantity,
            "timestamp": int(time.time() * 1000),
            "recvWindow": recv_window,
        }

        if order_type.upper() == "LIMIT":
            params["price"] = str(price)
            params["timeInForce"] = "GTC"

        # Sign
        params["signature"] = self._sign(params)

        logger.info("Placing order: %s %s %s qty=%s price=%s", symbol, side, order_type, quantity, price)

        try:
            resp = self.session.post(url, params=params, timeout=10)
        except requests.RequestException as e:
            logger.exception("Network error when placing order")
            raise BinanceAPIError(f"Network error: {e}") from e

        logger.info("Binance response status: %s body=%s", resp.status_code, resp.text)

        try:
            data = resp.json()
        except Exception as e:
            logger.exception("Failed to decode JSON response")
            raise BinanceAPIError(f"Invalid JSON response: {e}") from e

        if not resp.ok:
            msg = data.get("msg") or data.get("message") or resp.text
            logger.error("Binance API error: %s", msg)
            raise BinanceAPIError(f"API error: {msg}")

        return data


__all__ = ["BinanceFuturesClient", "BinanceAPIError"]
