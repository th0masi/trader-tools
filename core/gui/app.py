import asyncio
import logging
import sys

import qasync
from PyQt6.QtWidgets import QApplication

from .window import MainWindow


def run_app() -> None:
    """Точка входа в GUI-приложение."""
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    # delay=True — файл будет создан только при первом записанном сообщении
    file_handler = logging.FileHandler("trade_helper.log", encoding="utf-8", delay=True)
    file_handler.setLevel(logging.WARNING)

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[console_handler, file_handler],
    )

    app = QApplication(sys.argv)
    loop = qasync.QEventLoop(app)
    asyncio.set_event_loop(loop)

    main_window = MainWindow()
    main_window.show()

    with loop:
        sys.exit(loop.run_forever())


