# core/monitor.py
import asyncio
from dataclasses import dataclass
from typing import List, Dict, Tuple, Literal, Awaitable, Optional

from core.exchange.base import BaseClient

MarketType = Literal["spot", "perp"]


@dataclass
class Monitor:
    """
    Монитор, который агрегирует несколько клиентов бирж и запрашивает
    у них данные параллельно.
    """

    clients: List[BaseClient]

    async def query(
        self, token: str, market_type: MarketType
    ) -> Tuple[Dict[str, Tuple[str, float, str]], Dict[str, str]]:
        """
        Запрашивает данные у всех клиентов для указанного токена и типа рынка.
        Эта функция выполняет полный поиск символа.

        Возвращает словарь: {название_биржи: (символ, цена, url)}
        """
        results: Dict[str, Tuple[str, float, str]] = {}
        errors: Dict[str, str] = {}

        async def fetch_from_client(client: BaseClient) -> None:
            """Внутренняя функция для запроса данных от одного клиента."""
            price_coro: Optional[Awaitable[Optional[Tuple[str, float, str]]]] = None

            if market_type == "perp":
                price_coro = client.get_futures_price(token)
            elif market_type == "spot":
                price_coro = client.get_spot_price(token)

            if price_coro:
                try:
                    result = await price_coro
                    if result:
                        results[client.name] = result
                except Exception as e:
                    errors[client.name] = str(e)

        await asyncio.gather(*(fetch_from_client(c) for c in self.clients))
        return results, errors

    async def fetch_prices_for_known_symbols(
        self, known_symbols: Dict[str, str], market_type: MarketType
    ) -> Tuple[Dict[str, float], Dict[str, str]]:
        """
        Быстро запрашивает цены для уже известных символов без их повторного поиска.

        :param known_symbols: Словарь {название_биржи: символ}
        :param market_type: Тип рынка
        :return: Словарь {название_биржи: цена}
        """
        results: Dict[str, float] = {}
        errors: Dict[str, str] = {}
        client_map = {c.name: c for c in self.clients}

        async def fetch_for_client(client_name: str, symbol: str) -> None:
            """Внутренняя функция для запроса цены у одного клиента."""
            client = client_map.get(client_name)
            if not client:
                return

            price: Optional[float] = None
            try:
                if market_type == "perp":
                    price = await client.get_price_for_futures_symbol(symbol)
                elif market_type == "spot":
                    price = await client.get_price_for_spot_symbol(symbol)
            except Exception as e:
                errors[client_name] = str(e)
                return

            if price is not None:
                results[client_name] = price

        await asyncio.gather(
            *(
                fetch_for_client(name, sym)
                for name, sym in known_symbols.items()
            )
        )
        return results, errors