import logging
from typing import Optional, Tuple, List

import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class OkxClient(BaseClient):
    """Клиент OKX для спота и USDT-перпетуалов."""

    BASE_API = "https://www.okx.com/api/v5"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "okx"

    async def get_spot_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for instId in self._generate_spot(token):
            r = await self._request(
                "GET",
                f"{self.BASE_API}/market/ticker",
                request_name=f"okx spot {instId}",
                params={"instId": instId},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = (r.json() or {}).get("data") or []
            if not data:
                continue
            last = data[0].get("last")
            if last is None:
                continue
            return instId, float(last), self.get_spot_link(instId)
        return None

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            f"{self.BASE_API}/market/ticker",
            request_name=f"okx spot price {symbol}",
            params={"instId": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = (r.json() or {}).get("data") or []
        return float(data[0].get("last")) if data and data[0].get("last") else None

    def get_spot_link(self, instId: str) -> str:
        return f"https://www.okx.com/ru/trade-spot/{instId.replace('-', '-')}"

    async def get_futures_price(self, token: str) -> Optional[Tuple[str, float, str]]:
        for instId in self._generate_perp(token):
            r = await self._request(
                "GET",
                f"{self.BASE_API}/market/ticker",
                request_name=f"okx perp {instId}",
                params={"instId": instId},
                timeout=10,
            )
            if not r or r.status_code != 200:
                continue
            data = (r.json() or {}).get("data") or []
            if not data:
                continue
            last = data[0].get("last")
            if last is None:
                continue
            return instId, float(last), self.get_futures_link(instId)
        return None

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        r = await self._request(
            "GET",
            f"{self.BASE_API}/market/ticker",
            request_name=f"okx perp price {symbol}",
            params={"instId": symbol},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = (r.json() or {}).get("data") or []
        return float(data[0].get("last")) if data and data[0].get("last") else None

    def get_futures_link(self, instId: str) -> str:
        return f"https://www.okx.com/ru/trade-swap/{instId}"

    @staticmethod
    def _generate_spot(user_input: str) -> List[str]:
        s = user_input.strip().upper().replace(" ", "").replace("/", "-").replace("_", "-")
        if s.endswith("-USDT"):
            return [s]
        if s.endswith("USDT"):
            s = s[:-4]
        return [f"{s}-USDT"]

    @staticmethod
    def _generate_perp(user_input: str) -> List[str]:
        s = user_input.strip().upper().replace(" ", "").replace("/", "-").replace("_", "-")
        s = s.replace("PERP", "").replace("-USDT", "")
        return [f"{s}-USDT-SWAP"]


