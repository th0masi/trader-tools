import logging
from typing import Optional, Tuple, List

import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class BybitClient(BaseClient):
    """Клиент Bybit для спота и USDT-перпетуалов."""

    SPOT_API = "https://api.bybit.com/v5/market/tickers"
    FUT_API = "https://api.bybit.com/v5/market/tickers"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "bybit"

    async def get_spot_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._generate_spot(token):
            r = await self._request(
                "GET",
                self.SPOT_API,
                request_name=f"bybit spot {symbol}",
                params={"category": "spot", "symbol": symbol},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            result = (r.json() or {}).get("result") or {}
            lst = result.get("list") or []
            if not lst:
                continue
            price = lst[0].get("lastPrice") or lst[0].get("price")
            if price is None:
                continue
            return symbol, float(price), self.get_spot_link(symbol)
        return None

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            self.SPOT_API,
            request_name=f"bybit spot price {symbol}",
            params={"category": "spot", "symbol": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        result = (r.json() or {}).get("result") or {}
        lst = result.get("list") or []
        if not lst:
            return None
        price = lst[0].get("lastPrice") or lst[0].get("price")
        return float(price) if price is not None else None

    def get_spot_link(self, symbol: str) -> str:
        base = symbol.upper().replace("USDT", "")
        return f"https://www.bybit.com/spot/trade/{base}/USDT"

    async def get_futures_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._generate_perp(token):
            r = await self._request(
                "GET",
                self.FUT_API,
                request_name=f"bybit perp {symbol}",
                params={"category": "linear", "symbol": symbol},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            list_ = (r.json() or {}).get("result", {}).get("list") or []
            if not list_:
                continue
            price = list_[0].get("lastPrice")
            if price is None:
                continue
            return symbol, float(price), self.get_futures_link(symbol)
        return None

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            self.FUT_API,
            request_name=f"bybit perp price {symbol}",
            params={"category": "linear", "symbol": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        list_ = (r.json() or {}).get("result", {}).get("list") or []
        if not list_:
            return None
        price = list_[0].get("lastPrice")
        return float(price) if price is not None else None

    def get_futures_link(self, symbol: str) -> str:
        base = symbol.upper().replace("USDT", "")
        return f"https://www.bybit.com/trade/usdt/{base}USDT"

    @staticmethod
    def _generate_spot(user_input: str) -> List[str]:
        s = user_input.strip().upper().replace(" ", "").replace("-", "").replace("/", "")
        base = s[:-4] if s.endswith("USDT") else s
        return [f"{base}USDT"]

    @staticmethod
    def _generate_perp(user_input: str) -> List[str]:
        s = user_input.strip().upper().replace(" ", "").replace("-", "").replace("/", "")
        s = s.replace("PERP", "")
        base = s[:-4] if s.endswith("USDT") else s
        return [f"{base}USDT"]


