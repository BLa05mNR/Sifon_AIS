import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QFont
from UI.auth_window import AuthWindow


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Установка шрифта для всего приложения
    font = QFont()
    font.setFamily("Segoe UI")
    font.setStyleHint(QFont.SansSerif)
    app.setFont(font)

    window = AuthWindow()
    window.show()
    sys.exit(app.exec())