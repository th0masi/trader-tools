import asyncio
import logging
from typing import Optional, Tuple, Any
import httpx

logger = logging.getLogger(__name__)


class BaseClient:
    """
    Базовый класс для клиента биржи с механизмом повторов.
    Предоставляет универсальный `_request(...)` без вложенных функций.
    """

    name: str = "base"
    MAX_RETRIES: int = 3

    def __init__(self, http_client: httpx.AsyncClient):
        if not isinstance(http_client, httpx.AsyncClient):
            raise TypeError(
                "http_client должен быть экземпляром httpx.AsyncClient"
            )
        self.http_client = http_client

    @staticmethod
    def get_supported_exchanges() -> list[str]:
        """Справочный список поддерживаемых бирж (имена для QSettings)."""
        return [
            "gate",
            "hyperliquid",
            "binance",
            "okx",
            "bybit",
            "mexc",
            "bitget",
        ]

    async def _request(
        self,
        method: str,
        url: str,
        *,
        request_name: str,
        params: Optional[dict] = None,
        json: Optional[Any] = None,
        timeout: Optional[float] = None,
    ) -> Optional[httpx.Response]:
        """
        Выполняет HTTP-запрос с повторами. Возвращает ответ или None.
        Сетевые ошибки логируются. Статус-коды не поднимаются исключением.
        """
        for attempt in range(self.MAX_RETRIES):
            try:
                resp = await self.http_client.request(
                    method=method,
                    url=url,
                    params=params,
                    json=json,
                    timeout=timeout or 10,
                )
                return resp
            except httpx.RequestError as e:
                logger.error(
                    "[%s] Попытка %d/%d для '%s' провалена: %s",
                    self.name,
                    attempt + 1,
                    self.MAX_RETRIES,
                    request_name,
                    e,
                )
                if attempt + 1 < self.MAX_RETRIES:
                    await asyncio.sleep(1 + attempt)
        logger.error(
            "[%s] Все %d попытки для '%s' провалены.",
            self.name,
            self.MAX_RETRIES,
            request_name,
        )
        return None

    async def get_futures_price(
        self, token: str
    ) -> Optional[Tuple[str, float, str]]:
        """
        Находит фьючерсный рынок для токена и возвращает (символ, цена, url).
        """
        raise NotImplementedError

    async def get_price_for_futures_symbol(
        self, symbol: str
    ) -> Optional[float]:
        """Запрашивает цену для уже известного символа фьючерса."""
        raise NotImplementedError

    def get_futures_link(self, symbol: str) -> str:
        """Возвращает веб-ссылку на страницу торгов фьючерсом."""
        raise NotImplementedError

    async def get_spot_price(
        self, token: str
    ) -> Optional[Tuple[str, float, str]]:
        """
        Находит спотовый рынок для токена и возвращает (пара, цена, url).
        """
        raise NotImplementedError

    async def get_price_for_spot_symbol(self, symbol: str) -> Optional[float]:
        """Запрашивает цену для уже известного символа спотовой пары."""
        raise NotImplementedError

    def get_spot_link(self, pair: str) -> str:
        """Возвращает веб-ссылку на страницу торгов спотовой парой."""
        raise NotImplementedError