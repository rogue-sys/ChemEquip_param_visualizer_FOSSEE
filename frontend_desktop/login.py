"""
login.py
--------
Login screen widget.  Emits `login_successful` when the user authenticates,
or `register_requested` when the user clicks "Create Account".
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont

import api
from session import Session


class _LoginWorker(QThread):
    success = pyqtSignal(str)
    failure = pyqtSignal(str)

    def __init__(self, username, password):
        super().__init__()
        self._username = username
        self._password = password

    def run(self):
        try:
            token = api.login(self._username, self._password)
            self.success.emit(token)
        except api.APIError as e:
            self.failure.emit(str(e))


class LoginWidget(QWidget):
    login_successful   = pyqtSignal(str, str)
    register_requested = pyqtSignal()

    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self._worker = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget { background-color: #0e1117; color: #e8eaf0; }")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(16, 24, 16, 24)

        card = QFrame()
        card.setMaximumWidth(440)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1f2e;
                border-radius: 16px;
                border: 1px solid #2a2f3e;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 44, 40, 44)
        cl.setSpacing(0)

        icon = QLabel("⚗️")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 36))
        icon.setStyleSheet("border: none; background: transparent;")
        cl.addWidget(icon)

        title = QLabel("Chemical Equipment\nParameter Visualizer")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Georgia", 17, QFont.Bold))
        title.setStyleSheet("color: #00d4aa; border: none; background: transparent; margin-top: 8px;")
        cl.addWidget(title)

        subtitle = QLabel("Sign in to continue")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6b7280; font-size: 12px; border: none; background: transparent; margin-bottom: 28px;")
        cl.addWidget(subtitle)

        # Username
        self._field_label(cl, "USERNAME")
        self.username_input = self._input("Enter username")
        cl.addWidget(self.username_input)
        cl.addSpacing(14)

        # Password with show/hide toggle
        self._field_label(cl, "PASSWORD")
        self.password_input, pw_row = self._password_input("Enter password")
        self.password_input.returnPressed.connect(self._on_login_clicked)
        cl.addLayout(pw_row)
        cl.addSpacing(24)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #f76c6c; font-size: 11px; border: none; background: transparent; margin-bottom: 8px;")
        cl.addWidget(self.error_label)

        self.login_btn = QPushButton("Sign In")
        self.login_btn.setCursor(Qt.PointingHandCursor)
        self.login_btn.setFixedHeight(46)
        self.login_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.login_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #00d4aa, stop:1 #00a87d);
                color: #0e1117; border: none; border-radius: 10px;
            }
            QPushButton:hover   { background: #00e8bb; }
            QPushButton:pressed { background: #009e74; }
            QPushButton:disabled { background: #2a3040; color: #555; }
        """)
        self.login_btn.clicked.connect(self._on_login_clicked)
        cl.addWidget(self.login_btn)

        cl.addSpacing(20)

        # OR divider
        div = QHBoxLayout()
        left_line = QFrame()
        left_line.setFrameShape(QFrame.HLine)
        left_line.setStyleSheet("background-color: #2a2f3e; border: none; max-height: 1px;")
        or_lbl = QLabel("OR")
        or_lbl.setAlignment(Qt.AlignCenter)
        or_lbl.setFixedWidth(32)
        or_lbl.setStyleSheet("color: #4b5563; font-size: 10px; border: none; background: transparent;")
        right_line = QFrame()
        right_line.setFrameShape(QFrame.HLine)
        right_line.setStyleSheet("background-color: #2a2f3e; border: none; max-height: 1px;")
        div.addWidget(left_line)
        div.addWidget(or_lbl)
        div.addWidget(right_line)
        cl.addLayout(div)
        cl.addSpacing(16)

        self.register_btn = QPushButton("Create Account")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setFixedHeight(46)
        self.register_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #4f8ef7;
                border: 1.5px solid #4f8ef7; border-radius: 10px;
            }
            QPushButton:hover   { background: #4f8ef715; border-color: #6aa3ff; color: #6aa3ff; }
            QPushButton:pressed { background: #4f8ef725; }
            QPushButton:disabled { border-color: #2a3040; color: #555; }
        """)
        self.register_btn.clicked.connect(self.register_requested.emit)
        cl.addWidget(self.register_btn)

        cl.addSpacing(20)

        hint = QLabel("New here? Create a free account to start analysing\nchemical equipment parameters.")
        hint.setAlignment(Qt.AlignCenter)
        hint.setWordWrap(True)
        hint.setStyleSheet("color: #4b5563; font-size: 10px; border: none; background: transparent;")
        cl.addWidget(hint)

        outer.addWidget(card)

    def _field_label(self, layout, text):
        lbl = QLabel(text)
        lbl.setStyleSheet("color: #9ca3af; font-size: 10px; letter-spacing: 1px; font-weight: bold; border: none; background: transparent; margin-bottom: 4px;")
        layout.addWidget(lbl)

    def _input(self, placeholder):
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setFixedHeight(42)
        inp.setStyleSheet("""
            QLineEdit {
                background-color: #0e1117; border: 1.5px solid #2a2f3e;
                border-radius: 8px; padding: 0 14px; color: #e8eaf0; font-size: 13px;
            }
            QLineEdit:focus { border-color: #00d4aa; }
        """)
        return inp

    def _password_input(self, placeholder):
        """Returns (QLineEdit, QHBoxLayout) with an eye toggle button."""
        container = QFrame()
        container.setFixedHeight(42)
        container.setStyleSheet("""
            QFrame {
                background-color: #0e1117;
                border: 1.5px solid #2a2f3e;
                border-radius: 8px;
            }
            QFrame:focus-within { border-color: #00d4aa; }
        """)

        row = QHBoxLayout(container)
        row.setContentsMargins(14, 0, 6, 0)
        row.setSpacing(0)

        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        inp.setEchoMode(QLineEdit.Password)
        inp.setStyleSheet("""
            QLineEdit {
                background: transparent; border: none;
                color: #e8eaf0; font-size: 13px;
            }
        """)

        toggle_btn = QPushButton("👁")
        toggle_btn.setCursor(Qt.PointingHandCursor)
        toggle_btn.setFixedSize(32, 30)
        toggle_btn.setCheckable(True)
        toggle_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                color: #4b5563; font-size: 14px; padding: 0;
            }
            QPushButton:hover   { color: #9ca3af; }
            QPushButton:checked { color: #00d4aa; }
        """)

        def _toggle(checked):
            inp.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

        toggle_btn.toggled.connect(_toggle)

        row.addWidget(inp)
        row.addWidget(toggle_btn)

        # Wrap in a layout so it can be added to parent layout
        outer_row = QHBoxLayout()
        outer_row.setContentsMargins(0, 0, 0, 0)
        outer_row.addWidget(container)

        return inp, outer_row

    @pyqtSlot()
    def _on_login_clicked(self):
        username = self.username_input.text().strip()
        password = self.password_input.text()
        if not username or not password:
            self.error_label.setText("Please enter both username and password.")
            return
        self._set_loading(True)
        self.error_label.setText("")
        self._worker = _LoginWorker(username, password)
        self._worker.success.connect(lambda token: self._on_success(token, username))
        self._worker.failure.connect(self._on_failure)
        self._worker.start()

    def _on_success(self, token, username):
        self._set_loading(False)
        self.session.login(token, username)
        self.login_successful.emit(token, username)

    def _on_failure(self, message):
        self._set_loading(False)
        self.error_label.setText(message)

    def _set_loading(self, loading):
        self.login_btn.setEnabled(not loading)
        self.login_btn.setText("Signing in…" if loading else "Sign In")
        self.register_btn.setEnabled(not loading)
        self.username_input.setEnabled(not loading)
        self.password_input.setEnabled(not loading)

    def reset(self):
        self.username_input.clear()
        self.password_input.clear()
        self.error_label.setText("")
        self._set_loading(False)