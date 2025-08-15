import asyncio
import logging
from typing import Dict, Optional, Tuple

import httpx
from PyQt6.QtCore import (
    QDateTime,
    QPoint,
    QSettings,
    Qt,
    QTimer,
)
from PyQt6.QtGui import QBrush, QColor, QMouseEvent, QFont, QGuiApplication
from PyQt6.QtWidgets import (
    QComboBox,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QPushButton,
    QHBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QAbstractScrollArea,
)

from core.exchange.gate import GateClient
from core.exchange.hyperliquid import HyperliquidClient
from core.exchange.binance import BinanceClient
from core.exchange.okx import OkxClient
from core.exchange.bybit import BybitClient
from core.exchange.mexc import MexcClient
from core.exchange.bitget import BitgetClient
from core.exchange.base import BaseClient
from core.monitor import Monitor

from .settings import SettingsDialog
from .styles import DARK_STYLE, LIGHT_STYLE
from .utils import open_links_in_fresh_window, open_links_in_tabs
from .widgets import DragHandleLabel
import webbrowser
import re
import keyboard  # type: ignore


class MainWindow(QMainWindow):
    """Главное окно приложения с упрощенным управлением размером."""

    COMPACT_WIDTH = 385
    COMPACT_HEIGHT = 90
    MONITORING_WIDTH = 385
    MONITORING_HEIGHT = 350

    def __init__(self):
        super().__init__()
        self.settings = QSettings("CryptoMonitor", "App")
        self.worker_task: Optional[asyncio.Task] = None
        self.http_client: Optional[httpx.AsyncClient] = None
        self.old_pos: Optional[QPoint] = None
        self.known_symbols: Dict[str, str] = {}
        self.urls_map: Dict[str, str] = {}
        self.baseline_prices: Dict[str, float] = {}
        self.exchange_order = BaseClient.get_supported_exchanges()

        self.setup_ui()
        self.apply_settings()
        self._register_global_hotkey()

    def setup_ui(self):
        """Настройка интерфейса главного окна."""
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.main_layout = QVBoxLayout(self.main_widget)
        self.main_layout.setContentsMargins(10, 10, 10, 10)

        self.title_label = DragHandleLabel("<b>TradeHelper by ThorLab</b>")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.title_label)

        controls_layout = QHBoxLayout()
        controls_layout.setSpacing(10)

        self.token_input = QLineEdit()
        self.token_input.setPlaceholderText("Найти токен...")
        self.token_input.returnPressed.connect(self.start_monitoring)
        controls_layout.addWidget(self.token_input)

        self.market_type_combo = QComboBox()
        self.market_type_combo.addItems(["Futures", "Spot"])
        self.market_type_combo.setFixedWidth(110)
        controls_layout.addWidget(self.market_type_combo)

        self.settings_button: QPushButton = QPushButton("⚙️")
        self.settings_button.setFixedWidth(40)
        self.settings_button.clicked.connect(self.open_settings_dialog)
        controls_layout.addWidget(self.settings_button)

        self.main_layout.addLayout(controls_layout)

        self.stop_button: QPushButton = QPushButton("Stop")
        self.stop_button.setObjectName("stopButton")
        self.stop_button.clicked.connect(self.stop_monitoring)
        self.stop_button.hide()
        controls_layout.addWidget(self.stop_button)

        self.error_label = QLabel("")
        self.error_label.setObjectName("errorLabel")
        self.error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.error_label.hide()
        self.main_layout.addWidget(self.error_label)

        self.results_table = QTableWidget()
        self.results_table.setColumnCount(3)
        self.results_table.setHorizontalHeaderLabels(["Биржа", "Цена", "Δ %"])
        header = self.results_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.results_table.setColumnWidth(0, 130)
        self.results_table.setColumnWidth(1, 120)
        self.results_table.setColumnWidth(2, 110)
        self.results_table.verticalHeader().setVisible(False)
        self.results_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.results_table.setShowGrid(False)
        self.results_table.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_table.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_table.setSizeAdjustPolicy(QAbstractScrollArea.SizeAdjustPolicy.AdjustToContents)
        self.results_table.setSortingEnabled(False)
        header = self.results_table.horizontalHeader()
        header.setSortIndicatorShown(False)
        header.setSectionsClickable(False)
        self.results_table.hide()
        self.main_layout.addWidget(self.results_table)

        self.status_label = QLabel("")
        self.status_label.setObjectName("statusLabel")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_label.hide()
        self.main_layout.addWidget(self.status_label)

        self.setFixedSize(self.COMPACT_WIDTH, self.COMPACT_HEIGHT)
        self._apply_behavior_visibility()

    def apply_settings(self):
        """Применяет загруженные настройки к окну."""
        opacity = int(self.settings.value("window/opacity", 100)) / 100.0
        self.setWindowOpacity(opacity)
        theme = self.settings.value("window/theme", "Dark")
        style = DARK_STYLE if theme == "Dark" else LIGHT_STYLE
        self.setStyleSheet(style)
        self.main_widget.setStyleSheet(style)
        self._apply_behavior_visibility()
        self._register_global_hotkey()

    def _register_global_hotkey(self) -> None:
        """Регистрирует/снимает глобальный хоткей из настроек.
        Пустое значение — хоткей отключен."""
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
        combo = self.settings.value("hotkey/global", "") or ""
        combo = str(combo).strip()
        enabled = self.settings.value("hotkey/enable", False, type=bool)
        if not combo or not enabled:
            return
        try:
            keyboard.add_hotkey(combo, self._on_global_hotkey)
        except Exception as e:
            logging.warning(f"Не удалось установить глобальный хоткей '{combo}': {e}")

    def _on_global_hotkey(self) -> None:
        """Обработчик глобального хоткея. Делегирует в основной поток Qt."""
        QTimer.singleShot(0, self._trigger_from_clipboard)

    def _trigger_from_clipboard(self) -> None:
        """Запускает мониторинг, извлекая тикер из системного буфера обмена (в GUI-потоке)."""
        try:
            raw = QGuiApplication.clipboard().text() or ""
        except Exception:
            raw = ""
        token = self._extract_token_from_text(raw)
        if token:
            self.token_input.setText(token)
            self.start_monitoring()

    @staticmethod
    def _extract_token_from_text(text: str) -> str:
        """Извлекает тикер из произвольной строки/пары.
        - Удаляет ведущий $.
        - Принимает форматы: ETH_USDT, ETHUSDT, ETH-USD, ETH/USD.
        Возвращает тикер (ETH) либо пустую строку."""
        s = (text or "").strip()
        if not s:
            return ""
        if s.startswith("$"):
            s = s[1:]
        s = s.upper()
        m = re.match(r"^([A-Z0-9]+)[_\-/]?(USDT|USDC|USD)?$", s)
        if m:
            base = m.group(1)
            for q in ("USDT", "USDC", "USD"):
                if base.endswith(q):
                    base = base[: -len(q)]
                    break
            return base
        m2 = re.search(r"\b([A-Z0-9]{2,10})\b", s)
        return m2.group(1) if m2 else ""

    def open_settings_dialog(self):
        """Открывает диалог настроек."""
        dialog = SettingsDialog(self.settings, self)
        if dialog.exec():
            self.apply_settings()

    def set_monitoring_state(self, is_monitoring: bool):
        """Переключает состояние интерфейса и размер окна."""
        self.token_input.setVisible(not is_monitoring)
        self.market_type_combo.setVisible(not is_monitoring)
        self.settings_button.setVisible(not is_monitoring)
        self.stop_button.setVisible(is_monitoring)

        if is_monitoring:
            self.results_table.show()
            self.status_label.show()
            self.setFixedWidth(self.MONITORING_WIDTH)
            self.setMinimumHeight(self.MONITORING_HEIGHT)
            self.setMaximumHeight(16777215)
            self.adjustSize()
        else:
            self.results_table.hide()
            self.status_label.hide()
            self.setFixedSize(self.COMPACT_WIDTH, self.COMPACT_HEIGHT)

    def start_monitoring(self):
        """Запускает процесс мониторинга."""
        if self.worker_task and not self.worker_task.done():
            return

        token = self.token_input.text().strip().upper()
        if not token:
            self.show_error("Введите название токена.")
            return

        track_prices = self.settings.value("app/track_prices", True, type=bool)
        if track_prices:
            self.set_monitoring_state(True)
        self.error_label.hide()
        self.results_table.setRowCount(0)

        self.worker_task = asyncio.create_task(self.run_monitor_loop(token))

    def stop_monitoring(self):
        """Останавливает процесс мониторинга."""
        if self.worker_task and not self.worker_task.done():
            self.worker_task.cancel()
            logging.info("Мониторинг остановлен пользователем.")

    def show_error(self, message: str, duration: int = 3000):
        self.error_label.setText(message)
        self.error_label.show()
        QTimer.singleShot(duration, self.error_label.hide)

    async def run_monitor_loop(self, token: str):
        """Основная асинхронная логика поиска и обновления цен."""
        try:
            market_type = "perp" if self.market_type_combo.currentText() == "Futures" else "spot"
            enabled_exchanges = self.settings.value("app/exchanges", type=list)
            track_prices = self.settings.value("app/track_prices", True, type=bool)
            open_links_flag = self.settings.value("app/open_browser", False, type=bool)
            open_new_window = self.settings.value("links/new_window", True, type=bool)

            _TIMEOUT = int(self.settings.value("network/timeout", 10))
            _MAX_RETRIES = int(self.settings.value("network/retries", 3))

            self.http_client = httpx.AsyncClient()
            clients = []
            if "gate" in enabled_exchanges:
                clients.append(GateClient(self.http_client))
            if "binance" in enabled_exchanges:
                clients.append(BinanceClient(self.http_client))
            if "okx" in enabled_exchanges:
                clients.append(OkxClient(self.http_client))
            if "bybit" in enabled_exchanges:
                clients.append(BybitClient(self.http_client))
            if "mexc" in enabled_exchanges:
                clients.append(MexcClient(self.http_client))
            if "bitget" in enabled_exchanges:
                clients.append(BitgetClient(self.http_client))
            if "hyperliquid" in enabled_exchanges and market_type == 'perp':
                clients.append(HyperliquidClient(self.http_client))

            if not clients:
                self.show_error("Не выбрана ни одна биржа в настройках.")
                return

            mon = Monitor(clients=clients)
            logging.info(f"Начинаю поиск {token} на рынке {market_type}...")
            initial_data, initial_errors = await mon.query(token, market_type)

            if not initial_data and not initial_errors:
                self.show_error(f"Токен '{token}' не найден.", duration=10000)
                return

            self.known_symbols = {name: payload[0] for name, payload in initial_data.items()}
            self.urls_map = {name: payload[2] for name, payload in initial_data.items()}
            self.baseline_prices = {name: payload[1] for name, payload in initial_data.items()}

            if open_links_flag:
                urls = list(self.urls_map.values())
                if urls:
                    if open_new_window:
                        if not open_links_in_fresh_window(urls):
                            webbrowser.open_new(urls[0])
                            for url in urls[1:]:
                                webbrowser.open_new_tab(url)
                    else:
                        if not open_links_in_tabs(urls):
                            webbrowser.open_new(urls[0])
                            for url in urls[1:]:
                                webbrowser.open_new_tab(url)

            if not track_prices:
                return

            self.update_table(initial_data, errors=initial_errors)
            self.adjustSize()
            interval = int(self.settings.value("app/interval", 5))
            logging.info(f"Запуск обновления каждые {interval} сек.")

            while True:
                await asyncio.sleep(interval)
                new_prices, fetch_errors = await mon.fetch_prices_for_known_symbols(self.known_symbols, market_type)
                updated_data = {
                    name: (self.known_symbols[name], price, self.urls_map[name])
                    for name, price in new_prices.items() if name in self.known_symbols
                }
                self.update_table(updated_data, errors=fetch_errors)
                self.adjustSize()

        except asyncio.CancelledError:
            logging.info("Задача была отменена.")
        except Exception as e:
            logging.critical(f"Непредвиденная ошибка в воркере: {e}", exc_info=True)
            self.show_error("Произошла критическая ошибка. Подробности см. в логе.", duration=10000)
        finally:
            if self.http_client:
                await self.http_client.aclose()
            self.worker_task = None
            self.set_monitoring_state(False)

    def update_table(self, data: Dict[str, Tuple[str, float, str]], errors: Optional[Dict[str, str]] = None):
        """Обновляет QTableWidget без изменения размера окна."""
        errors = errors or {}
        current_time = QDateTime.currentDateTime().toString("HH:mm:ss.zzz")
        token = self.token_input.text().strip().upper()
        market_text = self.market_type_combo.currentText()
        status_text = f"{market_text} • {token} • Обновлено {current_time}"
        self.status_label.setText(status_text)

        all_names = list({*data.keys(), *errors.keys()})
        def _key(name: str) -> tuple:
            try:
                idx = self.exchange_order.index(name)
            except ValueError:
                idx = 999
            return (idx, name)
        all_names.sort(key=_key)
        self.results_table.setRowCount(len(all_names))
        for i, ex_name in enumerate(all_names):
            payload = data.get(ex_name)
            err_text = errors.get(ex_name)
            if payload:
                _, price, _ = payload
            else:
                price = None
            ex_item = QTableWidgetItem(ex_name.capitalize())
            self.results_table.setItem(i, 0, ex_item)

            base = self.baseline_prices.get(ex_name)
            delta = (price - base) / base * 100.0 if (price is not None and base and base > 0) else 0.0

            sign = "+" if delta > 0 else ""
            pct_text = f"{sign}{delta:.3f}%" if price is not None else ("ERROR" if err_text else "—")
            pct_item = QTableWidgetItem(pct_text)
            pct_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)

            font: QFont = pct_item.font()
            font.setBold(True)
            pct_item.setFont(font)
            if err_text:
                fg = QColor(255, 167, 38)  # оранжевый для ошибок
                bg = QColor(255, 167, 38, 30)
                pct_item.setForeground(QBrush(fg))
                pct_item.setBackground(QBrush(bg))
                pct_item.setToolTip(err_text)
            elif delta > 0:
                fg = QColor(0, 200, 83)  # ярко-зеленый
                bg = QColor(0, 200, 83, 30)
                pct_item.setForeground(QBrush(fg))
                pct_item.setBackground(QBrush(bg))
            elif delta < 0:
                fg = QColor(255, 82, 82)  # ярко-красный
                bg = QColor(255, 82, 82, 30)
                pct_item.setForeground(QBrush(fg))
                pct_item.setBackground(QBrush(bg))
            self.results_table.setItem(i, 2, pct_item)

            rich_text, is_rich = self._format_price(price) if price is not None else ("", False)
            lbl = QLabel()
            lbl.setTextFormat(Qt.TextFormat.RichText if is_rich else Qt.TextFormat.PlainText)
            lbl.setText(rich_text)
            lbl.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            lbl.setContentsMargins(5, 0, 0, 0)
            lbl.setStyleSheet("background: transparent; font-weight: 600;")
            self.results_table.setCellWidget(i, 1, lbl)

        self.results_table.resizeRowsToContents()
        self._adjust_table_height()

    def _adjust_table_height(self) -> None:
        """Подгоняет высоту таблицы под содержимое, убирая необходимость скролла."""
        header_h = self.results_table.horizontalHeader().height()
        rows_h = sum(self.results_table.rowHeight(r) for r in range(self.results_table.rowCount()))
        frame = 2  # границы таблицы
        total = header_h + rows_h + frame
        self.results_table.setFixedHeight(total)
        static_h = 120
        new_h = max(self.MONITORING_HEIGHT, static_h + total)
        self.setMinimumHeight(new_h)

    @staticmethod
    def _format_price(price: float) -> tuple[str, bool]:
        if price is None:
            return "", False
        if price >= 10:
            return f"{price:.2f}", False
        if price >= 0.1:
            return f"{price:.4f}", False
        s = f"{price:.12f}".rstrip('0')
        if '.' not in s:
            return s, False
        frac = s.split('.')[-1]
        zeros = 0
        for ch in frac:
            if ch == '0':
                zeros += 1
            else:
                break
        rest = frac[zeros:]
        if not rest:
            rest = '0'
        rich = f"<b>0.0<sub>{zeros}</sub>{rest}</b>"
        return rich, True

    def _apply_behavior_visibility(self):
        """Скрывает таблицу/статус при выключенном отслеживании цен."""
        track_prices = self.settings.value("app/track_prices", True, type=bool)
        if not track_prices:
            self.results_table.hide()
            self.status_label.hide()

    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.MouseButton.LeftButton:
            self.old_pos = event.globalPosition().toPoint()

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.old_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            delta = QPoint(event.globalPosition().toPoint() - self.old_pos)
            self.move(self.x() + delta.x(), self.y() + delta.y())
            self.old_pos = event.globalPosition().toPoint()

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.old_pos = None

    def closeEvent(self, event):
        self.stop_monitoring()
        super().closeEvent(event)
