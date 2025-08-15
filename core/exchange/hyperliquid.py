import logging
import re
from typing import Optional, Tuple, Set, Dict
import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class HyperliquidClient(BaseClient):
    """
    Клиент для Hyperliquid, использующий асинхронный httpx клиент.
    Поддерживает только фьючерсы (perpetuals).
    """

    INFO_API = "https://api.hyperliquid.xyz/info"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "hyperliquid"

    async def get_futures_price(
            self, token: str
    ) -> Optional[Tuple[str, float, str]]:
        universe = await self._fetch_universe()
        if not universe:
            return None

        coin = self._normalize_to_coin(token, universe)
        if not coin:
            logger.info(
                "[%s] Фьючерсы: токен '%s' не найден.",
                self.name,
                token,
            )
            return None

        price = await self.get_price_for_futures_symbol(coin)
        if price is None:
            logger.warning(
                "[%s] Фьючерсы: цена для '%s' недоступна.",
                self.name,
                coin,
            )
            return None

        url = self.get_futures_link(coin)
        return coin, price, url

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        """Запрашивает цену для уже известного символа фьючерса.
        У Hyperliquid некоторые тикеры префиксируются мультипликатором (например, kPEPE).
        В ответе allMids ключи соответствуют символам без приставки k в API ссылки.
        Поэтому всегда используем ключ ровно как symbol.upper()."""
        mids = await self._fetch_all_mids()
        if not mids:
            return None
        key = symbol.upper()
        return mids.get(key)

    def get_futures_link(self, symbol: str) -> str:
        return f"https://app.hyperliquid.xyz/trade/{symbol}"

    async def get_spot_price(
            self, token: str
    ) -> Optional[Tuple[str, float, str]]:
        logger.info("[%s] Спотовый рынок не поддерживается.", self.name)
        return None

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        return None

    def get_spot_link(self, pair: str) -> str:
        return ""

    async def _fetch_universe(self) -> Optional[Set[str]]:
        r = await self._request(
            "POST",
            self.INFO_API,
            request_name="получение списка активов (universe)",
            json={"type": "meta"},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json()
        universe = {
            asset.get("name", "").upper() for asset in data.get("universe", [])
        }
        return {u for u in universe if u}

    async def _fetch_all_mids(self) -> Optional[Dict[str, float]]:
        r = await self._request(
            "POST",
            self.INFO_API,
            request_name="получение всех цен (mids)",
            json={"type": "allMids"},
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json() or {}
        return {k.upper(): float(v) for k, v in data.items()}

    @staticmethod
    def _normalize_to_coin(
            user_input: str, universe: Set[str]
    ) -> Optional[str]:
        s = re.sub(r"[^A-Z0-9]", "", user_input.strip().upper().replace(
            "PERP", ""
        ))
        for quote in ("USDT", "USDC", "USD"):
            if s.endswith(quote):
                s = s[: -len(quote)]
        if s in universe:
            return s
        candidates = [u for u in universe if s in u]
        if len(candidates) == 1:
            return candidates[0]
        return None