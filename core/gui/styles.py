"""
Стили для приложения (темная и светлая темы).
"""

DARK_STYLE = """
    QWidget {
        background-color: #2b2b2b; color: #f0f0f0;
        font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt;
    }
    QMainWindow, QDialog { border: 1px solid #444; border-radius: 8px; }
    QGroupBox {
        border: 1px solid #444; border-radius: 8px; margin-top: 12px;
    }
    QGroupBox::title {
        subcontrol-origin: margin; left: 8px; padding: 0 4px;
    }
    QPushButton {
        background-color: #4a4a4a; border: 1px solid #555;
        border-radius: 5px; padding: 6px 12px;
    }
    QPushButton:hover { background-color: #5a5a5a; border-color: #666; }
    QPushButton:pressed { background-color: #3a3a3a; }
    QPushButton#stopButton { background-color: #8c4b4b; border-color: #a15c5c; }
    QPushButton#stopButton:hover { background-color: #a15c5c; }
    QLineEdit, QSpinBox {
        background-color: #3c3c3c; border: 1px solid #555;
        border-radius: 5px; padding: 6px;
    }
    QComboBox {
        background-color: #3c3c3c; border: 1px solid #555;
        border-radius: 5px; padding: 6px;
    }
    QComboBox:disabled { color: #8a8a8a; }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right; width: 20px;
        border: none;
    }
    QTableWidget {
        background-color: #3c3c3c; border: 1px solid #444;
        border-radius: 5px; gridline-color: #444;
    }
    QHeaderView::section { background-color: #2b2b2b; border: none; padding: 4px; }
    QSpinBox:disabled { color: #8a8a8a; }
    QLabel:disabled { color: #7a7a7a; }
    QCheckBox::indicator {
        width: 18px; height: 18px; border: 1px solid #777; border-radius: 4px;
        background-color: #3c3c3c;
    }
    QCheckBox::indicator:checked {
        background-color: #5a8dcf; border-color: #6aa1e6;
    }
    QLabel#errorLabel { color: #e57373; font-size: 9pt; }
    QLabel#statusLabel { font-size: 10pt; color: #aaa; }
"""


LIGHT_STYLE = """
    QWidget {
        background-color: #f0f0f0; color: #333;
        font-family: 'Segoe UI', Arial, sans-serif; font-size: 11pt;
    }
    QMainWindow, QDialog { border: 1px solid #ccc; border-radius: 8px; }
    QGroupBox {
        border: 1px solid #666; border-radius: 8px; margin-top: 12px;
    }
    QGroupBox::title {
        subcontrol-origin: margin; left: 8px; padding: 0 4px;
    }
    QPushButton {
        background-color: #e0e0e0; border: 1px solid #bbb;
        border-radius: 5px; padding: 6px 12px;
    }
    QPushButton:hover { background-color: #d0d0d0; border-color: #aaa; }
    QPushButton:pressed { background-color: #c0c0c0; }
    QPushButton#stopButton { background-color: #e57373; border-color: #d32f2f; }
    QPushButton#stopButton:hover { background-color: #ef9a9a; }
    QLineEdit, QSpinBox {
        background-color: #ffffff; border: 1px solid #ccc;
        border-radius: 5px; padding: 6px;
    }
    QComboBox {
        background-color: #ffffff; border: 1px solid #ccc;
        border-radius: 5px; padding: 6px;
    }
    QComboBox:disabled { color: #a0a0a0; }
    QComboBox::drop-down {
        subcontrol-origin: padding;
        subcontrol-position: top right; width: 20px;
        border: none;
    }
    QTableWidget {
        background-color: #ffffff; border: 1px solid #ddd;
        border-radius: 5px; gridline-color: #e0e0e0;
    }
    QHeaderView::section { background-color: #f0f0f0; border: none; padding: 4px; }
    QSpinBox:disabled { color: #a0a0a0; }
    QLabel:disabled { color: #9a9a9a; }
    QCheckBox::indicator {
        width: 18px; height: 18px; border: 2px solid #aaa; border-radius: 4px;
        background-color: #fff;
    }
    QCheckBox::indicator:checked {
        background-color: #4285f4; border-color: #4285f4;
    }
    QLabel#errorLabel { color: #d32f2f; font-size: 9pt; }
    QLabel#statusLabel { font-size: 10pt; color: #555; }
"""
