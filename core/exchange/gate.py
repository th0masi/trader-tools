import logging
from typing import Optional, Tuple, List
import httpx

from core.exchange.base import BaseClient

logger = logging.getLogger(__name__)


class GateClient(BaseClient):
    """
    Оптимизированный клиент для Gate.io, использующий прямые запросы к API
    для быстрой проверки существования пар и контрактов.
    """

    FX_API_BASE = "https://fx-api.gateio.ws/api/v4"
    SPOT_API_BASE = "https://api.gateio.ws/api/v4"
    SETTLE = "usdt"

    def __init__(self, http_client: httpx.AsyncClient):
        super().__init__(http_client)
        self.name = "gate"

    async def get_futures_price(
        self, token: str
    ) -> Optional[Tuple[str, float, str]]:
        """
        Находит фьючерсный контракт для токена и возвращает его первую цену.
        Возвращает (символ, цена, url).
        """
        candidate_symbols = self._generate_candidate_names(token)

        valid_symbol = None
        for symbol in candidate_symbols:
            if await self._is_valid_future(symbol):
                valid_symbol = symbol
                logger.info(
                    "[%s] Найден валидный фьючерсный контракт: %s",
                    self.name,
                    symbol,
                )
                break

        if not valid_symbol:
            logger.info(
                "[%s] Фьючерсы: не удалось найти валидный контракт для "
                "токена '%s'.",
                self.name,
                token,
            )
            return None

        price = await self.get_price_for_futures_symbol(valid_symbol)
        if price is None:
            return None

        url = self.get_futures_link(valid_symbol)
        return valid_symbol, price, url

    async def get_price_for_futures_symbol(self, symbol: str) -> Optional[float]:
        """Получает последнюю цену для конкретного фьючерса."""
        return await self._fetch_fx_last(symbol)

    def get_futures_link(self, symbol: str) -> str:
        return f"https://www.gate.com/futures/USDT/{symbol}"

    async def get_spot_price(
        self, token: str
    ) -> Optional[Tuple[str, float, str]]:
        """
        Находит спотовую пару для токена и возвращает её первую цену.
        Возвращает (пара, цена, url).
        """
        candidate_pairs = self._generate_candidate_names(token)

        valid_pair = None
        for pair in candidate_pairs:
            if await self._is_valid_spot_pair(pair):
                valid_pair = pair
                logger.info(
                    "[%s] Найдена валидная спотовая пара: %s",
                    self.name,
                    pair,
                )
                break

        if not valid_pair:
            logger.info(
                "[%s] Спот: не удалось найти валидную пару для токена "
                "'%s'.",
                self.name,
                token,
            )
            return None

        price = await self.get_price_for_spot_symbol(valid_pair)
        if price is None:
            return None

        url = self.get_spot_link(valid_pair)
        return valid_pair, price, url

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        """Получает последнюю цену для конкретной спотовой пары."""
        return await self._fetch_spot_last(symbol)

    def get_spot_link(self, pair: str) -> str:
        return f"https://www.gate.com/trade/{pair}"

    @staticmethod
    def _generate_candidate_names(user_input: str) -> List[str]:
        """Генерирует возможные имена для API из ввода пользователя."""
        s = (
            user_input.strip()
            .upper()
            .replace(" ", "")
            .replace("-", "_")
            .replace("/", "_")
        )
        if s.endswith("_USDT"):
            return [s]
        return [s + "_USDT"]

    async def _is_valid_future(self, contract: str) -> bool:
        """Проверяет существование фьючерсного контракта."""
        url = (
            f"{self.FX_API_BASE}/futures/{self.SETTLE}/contracts/{contract}"
        )
        r = await self._request(
            "GET",
            url,
            request_name=f"проверка фьючерса {contract}",
        )
        return bool(r and r.status_code == 200)

    async def _is_valid_spot_pair(self, pair: str) -> bool:
        """Проверяет существование спотовой пары."""
        url = f"{self.SPOT_API_BASE}/spot/currency_pairs/{pair}"
        r = await self._request(
            "GET",
            url,
            request_name=f"проверка спот-пары {pair}",
        )
        return bool(r and r.status_code == 200)

    async def _fetch_fx_last(self, contract: str) -> Optional[float]:
        """Получает последнюю цену для конкретного фьючерса."""
        url = f"{self.FX_API_BASE}/futures/{self.SETTLE}/tickers"
        params = {"contract": contract}
        r = await self._request(
            "GET",
            url,
            request_name=f"получение цены фьючерса {contract}",
            params=params,
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json()
        if data and "last" in data[0]:
            return float(data[0]["last"])
        return None

    async def _fetch_spot_last(self, pair: str) -> Optional[float]:
        """Получает последнюю цену для конкретной спотовой пары."""
        url = f"{self.SPOT_API_BASE}/spot/tickers"
        params = {"currency_pair": pair}
        r = await self._request(
            "GET",
            url,
            request_name=f"получение цены спота {pair}",
            params=params,
            timeout=10,
        )
        if not r or r.status_code != 200:
            return None
        data = r.json()
        if data and "last" in data[0]:
            return float(data[0]["last"])
        return None