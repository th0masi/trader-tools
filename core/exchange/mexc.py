import logging
from typing import Optional, Tuple, List

import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class MexcClient(BaseClient):
    """Клиент MEXC для спота и USDT-перпетуалов."""

    SPOT_API = "https://api.mexc.com/api/v3/ticker/price"
    FUT_API = "https://contract.mexc.com/api/v1/contract/ticker"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "mexc"

    async def get_spot_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._gen_spot(token):
            r = await self._request(
                "GET",
                self.SPOT_API,
                request_name=f"mexc spot {symbol}",
                params={"symbol": symbol},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = r.json() or {}
            price = data.get("price")
            if price is None:
                continue
            return symbol, float(price), self.get_spot_link(symbol)
        return None

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            self.SPOT_API,
            request_name=f"mexc spot price {symbol}",
            params={"symbol": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json() or {}
        price = data.get("price")
        return float(price) if price is not None else None

    def get_spot_link(self, symbol: str) -> str:
        base = symbol.upper().replace("USDT", "")
        return f"https://www.mexc.com/exchange/{base}_USDT"

    async def get_futures_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for symbol in self._gen_perp(token):
            r = await self._request(
                "GET",
                self.FUT_API,
                request_name=f"mexc perp {symbol}",
                params={"symbol": symbol},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            payload = r.json() or {}
            data = payload.get("data")
            entry = None
            if isinstance(data, list):
                entry = data[0] if data else None
            elif isinstance(data, dict):
                entry = data
            if not entry:
                continue
            price = entry.get("lastPrice") or entry.get("last")
            if price is None:
                continue
            return symbol, float(price), self.get_futures_link(symbol)
        return None

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            self.FUT_API,
            request_name=f"mexc perp price {symbol}",
            params={"symbol": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        payload = r.json() or {}
        data = payload.get("data")
        entry = None
        if isinstance(data, list):
            entry = data[0] if data else None
        elif isinstance(data, dict):
            entry = data
        if not entry:
            return None
        price = entry.get("lastPrice") or entry.get("last")
        return float(price) if price is not None else None

    def get_futures_link(self, symbol: str) -> str:
        sym = symbol.upper()
        if sym.endswith("USDT") and "_" not in sym:
            sym = sym.replace("USDT", "_USDT")
        return f"https://futures.mexc.com/exchange/{sym}"

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
        candidates = [
            f"{base}USDT",        # ETHUSDT
            f"{base}_USDT",       # ETH_USDT (часто в MEXC фьючах)
        ]
        return candidates


