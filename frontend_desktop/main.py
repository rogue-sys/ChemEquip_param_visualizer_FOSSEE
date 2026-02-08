# main.py
import sys
from PyQt5.QtWidgets import QApplication
from login import LoginWindow


APP_QSS = """
* {
    font-family: "Segoe UI";
    font-size: 14px;
}

QWidget {
    background-color: #0f172a;
    color: #e5e7eb;
}

QLineEdit {
    padding: 10px;
    border-radius: 8px;
    border: 1px solid #334155;
    background: #020617;
}

QLineEdit:focus {
    border: 1px solid #38bdf8;
}

QPushButton {
    padding: 10px;
    border-radius: 8px;
    background-color: #2563eb;
}

QPushButton:hover {
    background-color: #1d4ed8;
}

QPushButton:disabled {
    background-color: #475569;
}

QLabel#error {
    color: #f87171;
}
"""


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyleSheet(APP_QSS)

    win = LoginWindow()
    win.show()

    sys.exit(app.exec_())
