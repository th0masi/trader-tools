import logging
from typing import Optional, Tuple, List

import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class BitgetClient(BaseClient):
    """Клиент Bitget для спота и USDT-перпетуалов."""

    BASE_API = "https://api.bitget.com/api"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "bitget"

    async def get_spot_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._gen_spot(token):
            r = await self._request(
                "GET",
                f"{self.BASE_API}/spot/v1/market/tickers",
                request_name=f"bitget spot {symbol}",
                params={"symbol": symbol},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = (r.json() or {}).get("data") or []
            entry = None
            for item in data:
                if item.get("symbol") == symbol:
                    entry = item
                    break
            if not entry:
                continue
            price = entry.get("close") or entry.get("last")
            if price is None:
                continue
            return symbol, float(price), self.get_spot_link(symbol)
        return None

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            f"{self.BASE_API}/spot/v1/market/tickers",
            request_name=f"bitget spot price {symbol}",
            params={"symbol": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = (r.json() or {}).get("data") or []
        entry = None
        for item in data:
            if item.get("symbol") == symbol:
                entry = item
                break
        if not entry:
            return None
        price = entry.get("close") or entry.get("last")
        return float(price) if price is not None else None

    def get_spot_link(self, symbol: str) -> str:
        base = symbol.upper().replace("USDT", "")
        return f"https://www.bitget.com/spot/{base}USDT_SPBL"

    async def get_futures_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._gen_perp(token):
            r = await self._request(
                "GET",
                f"{self.BASE_API}/mix/v1/market/ticker",
                request_name=f"bitget perp {symbol}",
                params={"symbol": symbol, "productType": "umcbl"},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = (r.json() or {}).get("data") or {}
            price = data.get("last")
            if price is None:
                continue
            return symbol, float(price), self.get_futures_link(symbol)
        return None

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            f"{self.BASE_API}/mix/v1/market/ticker",
            request_name=f"bitget perp price {symbol}",
            params={"symbol": symbol, "productType": "umcbl"},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = (r.json() or {}).get("data") or {}
        price = data.get("last")
        return float(price) if price is not None else None

    def get_futures_link(self, symbol: str) -> str:
        return f"https://www.bitget.com/futures/usdt/{symbol}"

    @staticmethod
    def _gen_spot(user_input: str) -> List[str]:
        s = user_input.strip().upper().replace(" ", "").replace("-", "").replace("/", "")
        if s.endswith("USDT"):
            return [s]
        return [f"{s}USDT"]

    @staticmethod
    def _gen_perp(user_input: str) -> List[str]:
        s = user_input.strip().upper().replace(" ", "").replace("-", "").replace("/", "")
        s = s.replace("PERP", "")
        base = s[:-4] if s.endswith("USDT") else s
        return [f"{base}USDT_UMCBL"]


