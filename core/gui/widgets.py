from PyQt6.QtCore import Qt
from PyQt6.QtGui import QMouseEvent
from PyQt6.QtWidgets import QLabel, QLineEdit


class DragHandleLabel(QLabel):
    """Метка, которая передает события мыши родительскому окну для перетаскивания."""

    def mousePressEvent(self, event: QMouseEvent):
        self.window().mousePressEvent(event)

    def mouseMoveEvent(self, event: QMouseEvent):
        self.window().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.window().mouseReleaseEvent(event)


class HotkeyLineEdit(QLineEdit):
    """Поле ввода, которое перехватывает нажатия клавиш и формирует строку хоткея.
    - ЛКМ используется только для фокуса, не влияет на хоткей
    - Enter/Return подтверждает ввод (не добавляется в комбинацию)
    - Esc очищает поле
    """

    def keyPressEvent(self, event):
        key = event.key()
        if key in (Qt.Key.Key_Return, Qt.Key.Key_Enter):
            self.clearFocus()
            return
        if key == Qt.Key.Key_Escape:
            self.setText("")
            return
        if key in (
            Qt.Key.Key_Control,
            Qt.Key.Key_Shift,
            Qt.Key.Key_Alt,
            Qt.Key.Key_Meta,
        ):
            return

        parts = []
        mods = event.modifiers()
        if mods & Qt.KeyboardModifier.ControlModifier:
            parts.append("ctrl")
        if mods & Qt.KeyboardModifier.AltModifier:
            parts.append("alt")
        if mods & Qt.KeyboardModifier.ShiftModifier:
            parts.append("shift")
        if mods & Qt.KeyboardModifier.MetaModifier:
            parts.append("meta")

        name = None
        if Qt.Key.Key_A <= key <= Qt.Key.Key_Z:
            name = chr(ord('a') + (key - Qt.Key.Key_A))
        elif Qt.Key.Key_0 <= key <= Qt.Key.Key_9:
            name = chr(ord('0') + (key - Qt.Key.Key_0))
        elif Qt.Key.Key_F1 <= key <= Qt.Key.Key_F24:
            name = f"f{1 + (key - Qt.Key.Key_F1)}"
        elif key == Qt.Key.Key_Space:
            name = "space"
        elif key == Qt.Key.Key_Tab:
            name = "tab"
        else:
            text = (event.text() or "").strip()
            if text:
                name = text.lower()
        if not name:
            return

        parts.append(name)
        self.setText("+".join(parts))


