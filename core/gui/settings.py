from typing import Optional

from PyQt6.QtCore import QSettings, Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QFormLayout,
    QGroupBox,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSlider,
    QSpinBox,
    QAbstractSpinBox,
    QVBoxLayout,
)
from .widgets import HotkeyLineEdit


class SettingsDialog(QDialog):
    """Диалоговое окно для всех настроек (без изменений, кроме стилей)."""

    def __init__(self, settings: QSettings, parent: Optional[object] = None):
        super().__init__(parent)
        self.settings = settings
        self.setWindowTitle("Настройки")
        self.setModal(True)
        self.setMinimumWidth(350)

        self.opacity_slider = QSlider(Qt.Orientation.Horizontal)
        self.opacity_slider.setRange(20, 100)
        self.opacity_label = QLabel()
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Light", "Dark"])

        self.hotkey_edit = HotkeyLineEdit()
        self.hotkey_edit.setPlaceholderText("Не задано")
        self.autostart_check = QCheckBox("Автостарт из буфера")

        self.interval_spin = QSpinBox()
        self.interval_spin.setRange(1, 3600)
        self.interval_spin.setSuffix(" сек")
        self.track_prices_check = QCheckBox("Отслеживать цены")

        self.timeout_spin = QSpinBox()
        self.timeout_spin.setRange(1, 60)
        self.timeout_spin.setSuffix(" сек")
        self.retries_spin = QSpinBox()
        self.retries_spin.setRange(0, 10)

        self.interval_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.timeout_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        self.retries_spin.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)

        self.gate_check = QCheckBox("Gate.io")
        self.hyperliquid_check = QCheckBox("Hyperliquid")
        self.binance_check = QCheckBox("Binance")
        self.okx_check = QCheckBox("OKX")
        self.bybit_check = QCheckBox("Bybit")
        self.mexc_check = QCheckBox("MEXC")
        self.bitget_check = QCheckBox("Bitget")

        self.open_browser_check = QCheckBox("Открывать ссылки в браузере")
        self.links_open_mode_combo = QComboBox()
        self.links_open_mode_combo.addItems([
            "В новом окне",
            "Во вкладках существующего окна",
        ])
        self.links_mode_label = QLabel("Как открывать:")

        self.save_button: QPushButton = QPushButton("Сохранить и закрыть")
        self.save_button.clicked.connect(self.save_and_accept)

        self.load_settings()

        layout = QVBoxLayout(self)
        appearance_group = QGroupBox("Внешний вид")
        form_layout1 = QFormLayout()
        opacity_layout = QHBoxLayout()
        opacity_layout.addWidget(self.opacity_slider)
        opacity_layout.addWidget(self.opacity_label)
        form_layout1.addRow("Прозрачность:", opacity_layout)
        form_layout1.addRow("Тема:", self.theme_combo)
        appearance_group.setLayout(form_layout1)
        layout.addWidget(appearance_group)

        hotkey_group = QGroupBox("Автостарт")
        hotkey_group.setToolTip("Скопируйте в буфер тикер (например, ETH), затем нажмите хоткей — софт запустит поиск автоматически.")
        hotkey_form = QFormLayout()
        hotkey_form.addRow(self.autostart_check)
        hotkey_form.addRow("Хоткей:", self.hotkey_edit)
        hotkey_group.setLayout(hotkey_form)
        layout.addWidget(hotkey_group)

        behavior_group = QGroupBox("Цены")
        form_layout2 = QFormLayout()
        form_layout2.addRow(self.track_prices_check)
        form_layout2.addRow("Интервал обновления:", self.interval_spin)
        behavior_group.setLayout(form_layout2)
        layout.addWidget(behavior_group)

        links_group = QGroupBox("Браузер")
        links_v = QVBoxLayout()
        links_v.addWidget(self.open_browser_check)
        links_form = QFormLayout()
        links_form.addRow(self.links_mode_label, self.links_open_mode_combo)
        links_v.addLayout(links_form)
        links_group.setLayout(links_v)
        layout.addWidget(links_group)

        exchanges_group = QGroupBox("Биржи")
        grid = QGridLayout()
        checks = [
            self.gate_check,
            self.hyperliquid_check,
            self.binance_check,
            self.okx_check,
            self.bybit_check,
            self.mexc_check,
            self.bitget_check,
        ]
        for i, cb in enumerate(checks):
            row, col = divmod(i, 3)
            grid.addWidget(cb, row, col)
        exchanges_group.setLayout(grid)
        layout.addWidget(exchanges_group)

        network_group = QGroupBox("API запросы")
        form_layout3 = QFormLayout()
        form_layout3.addRow("Таймаут запроса:", self.timeout_spin)
        form_layout3.addRow("Макс. попыток:", self.retries_spin)
        network_group.setLayout(form_layout3)
        layout.addWidget(network_group)

        dev_group = QGroupBox("Разработчик")
        dev_layout = QVBoxLayout()
        dev_label = QLabel(
            'Oleg th0masi → <a style="color:#1E88E5;" href="https://t.me/thor_lab">t.me/thor_lab</a>'
        )
        dev_label.setOpenExternalLinks(True)
        dev_layout.addWidget(dev_label)
        dev_group.setLayout(dev_layout)
        layout.addWidget(dev_group)

        layout.addStretch()
        layout.addWidget(self.save_button, alignment=Qt.AlignmentFlag.AlignRight)
        self.opacity_slider.valueChanged.connect(self.update_opacity)
        self.track_prices_check.toggled.connect(self._on_track_prices_toggled)
        self.open_browser_check.toggled.connect(self._on_open_links_toggled)
        self._on_autostart_toggled(self.autostart_check.isChecked())

    def load_settings(self):
        opacity = int(self.settings.value("window/opacity", 100))
        self.opacity_slider.setValue(opacity)
        self.opacity_label.setText(f"{opacity}%")
        self.theme_combo.setCurrentText(self.settings.value("window/theme", "Dark"))
        self.hotkey_edit.setText(self.settings.value("hotkey/global", ""))
        self.autostart_check.setChecked(self.settings.value("hotkey/enable", False, type=bool))
        self.interval_spin.setValue(int(self.settings.value("app/interval", 5)))
        self.track_prices_check.setChecked(self.settings.value("app/track_prices", True, type=bool))
        self.open_browser_check.setChecked(self.settings.value("app/open_browser", False, type=bool))
        new_window = self.settings.value("links/new_window", True, type=bool)
        self.links_open_mode_combo.setCurrentIndex(0 if new_window else 1)
        enabled_exchanges = self.settings.value(
            "app/exchanges",
            ["gate", "binance", "bybit", "okx", "mexc", "bitget", "hyperliquid"],
            type=list,
        )
        self.gate_check.setChecked("gate" in enabled_exchanges)
        self.hyperliquid_check.setChecked("hyperliquid" in enabled_exchanges)
        self.binance_check.setChecked("binance" in enabled_exchanges)
        self.okx_check.setChecked("okx" in enabled_exchanges)
        self.bybit_check.setChecked("bybit" in enabled_exchanges)
        self.mexc_check.setChecked("mexc" in enabled_exchanges)
        self.bitget_check.setChecked("bitget" in enabled_exchanges)
        self.timeout_spin.setValue(int(self.settings.value("network/timeout", 10)))
        self.retries_spin.setValue(int(self.settings.value("network/retries", 3)))

        self._on_track_prices_toggled(self.track_prices_check.isChecked())
        self._on_open_links_toggled(self.open_browser_check.isChecked())

    def update_opacity(self, value):
        self.opacity_label.setText(f"{value}%")
        self.parent().setWindowOpacity(value / 100.0)

    def save_and_accept(self):
        self.settings.setValue("window/opacity", self.opacity_slider.value())
        self.settings.setValue("window/theme", self.theme_combo.currentText())
        self.settings.setValue("hotkey/global", self.hotkey_edit.text().strip())
        self.settings.setValue("hotkey/enable", self.autostart_check.isChecked())
        self.settings.setValue("app/interval", self.interval_spin.value())
        self.settings.setValue("app/track_prices", self.track_prices_check.isChecked())
        self.settings.setValue("app/open_browser", self.open_browser_check.isChecked())
        self.settings.setValue("links/new_window", self.links_open_mode_combo.currentIndex() == 0)
        enabled_exchanges = []
        if self.gate_check.isChecked(): enabled_exchanges.append("gate")
        if self.hyperliquid_check.isChecked(): enabled_exchanges.append("hyperliquid")
        if self.binance_check.isChecked(): enabled_exchanges.append("binance")
        if self.okx_check.isChecked(): enabled_exchanges.append("okx")
        if self.bybit_check.isChecked(): enabled_exchanges.append("bybit")
        if self.mexc_check.isChecked(): enabled_exchanges.append("mexc")
        if self.bitget_check.isChecked(): enabled_exchanges.append("bitget")
        self.settings.setValue("app/exchanges", enabled_exchanges)
        self.settings.setValue("network/timeout", self.timeout_spin.value())
        self.settings.setValue("network/retries", self.retries_spin.value())
        self.accept()

    def _on_track_prices_toggled(self, checked: bool):
        self.interval_spin.setEnabled(checked)

    def _on_open_links_toggled(self, checked: bool):
        self.links_open_mode_combo.setEnabled(checked)
        self.links_mode_label.setEnabled(checked)

    def _on_autostart_toggled(self, checked: bool):
        self.hotkey_edit.setEnabled(checked)



