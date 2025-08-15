import logging
from typing import Optional, Tuple, List

import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class BinanceClient(BaseClient):
    """Клиент Binance для спота и USDT-перпетуалов."""

    SPOT_API = "https://api.binance.com/api/v3/ticker/price"
    FUT_API = "https://fapi.binance.com/fapi/v1/ticker/price"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "binance"

    async def get_spot_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._generate_candidate_symbols(token):
            params = {"symbol": symbol}
            r = await self._request(
                "GET",
                self.SPOT_API,
                request_name=f"binance spot {symbol}",
                params=params,
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = r.json()
            price = float(data.get("price")) if data and data.get("price") else None
            if price is None:
                continue
            url = self.get_spot_link(symbol)
            return symbol, price, url
        return None

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        params = {"symbol": symbol}
        r = await self._request(
            "GET",
            self.SPOT_API,
            request_name=f"binance spot price {symbol}",
            params=params,
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json()
        return float(data.get("price")) if data and data.get("price") else None

    def get_spot_link(self, symbol: str) -> str:
        base = symbol.upper().replace("USDT", "")
        return f"https://www.binance.com/en/trade/{base}_USDT?type=spot"

    async def get_futures_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._generate_candidate_symbols(token):
            params = {"symbol": symbol}
            r = await self._request(
                "GET",
                self.FUT_API,
                request_name=f"binance fut {symbol}",
                params=params,
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = r.json()
            price = float(data.get("price")) if data and data.get("price") else None
            if price is None:
                continue
            url = self.get_futures_link(symbol)
            return symbol, price, url
        return None

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        params = {"symbol": symbol}
        r = await self._request(
            "GET",
            self.FUT_API,
            request_name=f"binance fut price {symbol}",
            params=params,
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json()
        return float(data.get("price")) if data and data.get("price") else None

    def get_futures_link(self, symbol: str) -> str:
        base = symbol.upper().replace("USDT", "")
        return f"https://www.binance.com/en/futures/{base}USDT"

    @staticmethod
    def _generate_candidate_symbols(user_input: str) -> List[str]:
        s = (
            user_input.strip().upper().replace(" ", "").replace("-", "").replace("/", "")
        )
        if s.endswith("USDT"):
            return [s]
        return [f"{s}USDT"]


