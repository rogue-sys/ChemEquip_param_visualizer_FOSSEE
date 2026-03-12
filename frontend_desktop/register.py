"""
register.py  —  Registration screen widget.
Responsive fix: card uses setMaximumWidth, not setFixedWidth.
"""

import re
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont

import api


class _RegisterWorker(QThread):
    success = pyqtSignal(dict)
    failure = pyqtSignal(str)

    def __init__(self, username, password):
        super().__init__()
        self._username = username
        self._password = password

    def run(self):
        try:
            result = api.register(self._username, self._password)
            self.success.emit(result)
        except api.APIError as e:
            self.failure.emit(str(e))


def _password_strength(pwd):
    if not pwd:
        return 0, "", "#2a2f3e"
    score = sum([
        len(pwd) >= 8,
        bool(re.search(r"[A-Z]", pwd)),
        bool(re.search(r"[0-9]", pwd)),
        bool(re.search(r"[^A-Za-z0-9]", pwd)),
    ])
    labels = {0: "Weak", 1: "Fair", 2: "Good", 3: "Strong"}
    colors = {0: "#f76c6c", 1: "#f7c948", 2: "#4f8ef7", 3: "#00d4aa"}
    return score, labels[score], colors[score]


class RegisterWidget(QWidget):
    register_successful = pyqtSignal(str, str)
    back_to_login       = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._worker = None
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget { background-color: #0e1117; color: #e8eaf0; }")

        outer = QVBoxLayout(self)
        outer.setAlignment(Qt.AlignCenter)
        outer.setContentsMargins(16, 24, 16, 24)

        card = QFrame()
        card.setMaximumWidth(460)
        card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1f2e;
                border-radius: 16px;
                border: 1px solid #2a2f3e;
            }
        """)
        cl = QVBoxLayout(card)
        cl.setContentsMargins(40, 40, 40, 40)
        cl.setSpacing(0)

        icon = QLabel("⚗️")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 32))
        icon.setStyleSheet("border: none; background: transparent;")
        cl.addWidget(icon)

        title = QLabel("Create Account")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #00d4aa; border: none; background: transparent; margin-top: 6px;")
        cl.addWidget(title)

        subtitle = QLabel("Join the Chemical Equipment Visualizer")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #6b7280; font-size: 11px; border: none; background: transparent; margin-bottom: 24px;")
        cl.addWidget(subtitle)

        # Username
        self._field_label(cl, "USERNAME")
        self.username_input = self._input("Choose a username")
        self.username_input.textChanged.connect(self._validate_username_live)
        cl.addWidget(self.username_input)
        self.username_hint = self._hint()
        cl.addWidget(self.username_hint)
        cl.addSpacing(14)

        # Password with show/hide toggle
        self._field_label(cl, "PASSWORD")
        self.password_input, pw_row = self._password_input("Create a password")
        self.password_input.textChanged.connect(self._on_password_changed)
        cl.addLayout(pw_row)

        # Strength bar
        self.strength_bar_bg = QFrame()
        self.strength_bar_bg.setFixedHeight(4)
        self.strength_bar_bg.setStyleSheet("background: #2a2f3e; border-radius: 2px; border: none;")
        bg_inner = QHBoxLayout(self.strength_bar_bg)
        bg_inner.setContentsMargins(0, 0, 0, 0)
        self.strength_bar = QFrame()
        self.strength_bar.setFixedHeight(4)
        self.strength_bar.setStyleSheet("background: #2a2f3e; border-radius: 2px; border: none;")
        bg_inner.addWidget(self.strength_bar)
        bg_inner.addStretch()
        cl.addWidget(self.strength_bar_bg)
        self.strength_label = self._hint()
        cl.addWidget(self.strength_label)
        cl.addSpacing(14)

        # Confirm password with show/hide toggle
        self._field_label(cl, "CONFIRM PASSWORD")
        self.confirm_input, cf_row = self._password_input("Re-enter your password")
        self.confirm_input.textChanged.connect(self._validate_confirm_live)
        self.confirm_input.returnPressed.connect(self._on_register_clicked)
        cl.addLayout(cf_row)
        self.confirm_hint = self._hint()
        cl.addWidget(self.confirm_hint)
        cl.addSpacing(20)

        self.error_label = QLabel("")
        self.error_label.setAlignment(Qt.AlignCenter)
        self.error_label.setWordWrap(True)
        self.error_label.setStyleSheet("color: #f76c6c; font-size: 11px; border: none; background: transparent; margin-bottom: 8px;")
        cl.addWidget(self.error_label)

        self.register_btn = QPushButton("Create Account")
        self.register_btn.setCursor(Qt.PointingHandCursor)
        self.register_btn.setFixedHeight(46)
        self.register_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        self.register_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0, stop:0 #4f8ef7, stop:1 #2c6cf5);
                color: #ffffff; border: none; border-radius: 10px;
            }
            QPushButton:hover   { background: #6aa3ff; }
            QPushButton:pressed { background: #2058d0; }
            QPushButton:disabled { background: #2a3040; color: #555; }
        """)
        self.register_btn.clicked.connect(self._on_register_clicked)
        cl.addWidget(self.register_btn)

        cl.addSpacing(20)

        back_row = QHBoxLayout()
        already = QLabel("Already have an account?")
        already.setStyleSheet("color: #6b7280; font-size: 11px; border: none; background: transparent;")
        signin_btn = QPushButton("Sign In")
        signin_btn.setCursor(Qt.PointingHandCursor)
        signin_btn.setFlat(True)
        signin_btn.setStyleSheet("QPushButton { color: #00d4aa; font-size: 11px; font-weight: bold; border: none; background: transparent; padding: 0; } QPushButton:hover { color: #00e8bb; }")
        signin_btn.clicked.connect(self.back_to_login.emit)
        back_row.addStretch()
        back_row.addWidget(already)
        back_row.addSpacing(4)
        back_row.addWidget(signin_btn)
        back_row.addStretch()
        cl.addLayout(back_row)

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
            QLineEdit:focus { border-color: #4f8ef7; }
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
            QFrame:focus-within { border-color: #4f8ef7; }
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
            QPushButton:checked { color: #4f8ef7; }
        """)

        def _toggle(checked):
            inp.setEchoMode(QLineEdit.Normal if checked else QLineEdit.Password)

        toggle_btn.toggled.connect(_toggle)

        row.addWidget(inp)
        row.addWidget(toggle_btn)

        outer_row = QHBoxLayout()
        outer_row.setContentsMargins(0, 0, 0, 0)
        outer_row.addWidget(container)

        return inp, outer_row

    def _hint(self):
        lbl = QLabel("")
        lbl.setStyleSheet("font-size: 10px; border: none; background: transparent; margin-top: 2px;")
        lbl.setFixedHeight(14)
        return lbl

    def _set_hint(self, lbl, text, color):
        lbl.setText(text)
        lbl.setStyleSheet(f"color: {color}; font-size: 10px; border: none; background: transparent; margin-top: 2px;")

    def _validate_username_live(self, text):
        if not text:
            self.username_hint.setText(""); return
        if len(text) < 3:
            self._set_hint(self.username_hint, "At least 3 characters required", "#f7c948")
        elif not re.match(r"^[A-Za-z0-9_]+$", text):
            self._set_hint(self.username_hint, "Only letters, numbers and underscores", "#f76c6c")
        else:
            self._set_hint(self.username_hint, "✓ Looks good", "#00d4aa")

    def _on_password_changed(self, text):
        score, label, color = _password_strength(text)
        if score == 0:
            self.strength_bar.setFixedWidth(0)
            self.strength_label.setText("")
        else:
            self.strength_bar.setFixedWidth(int(360 * score / 4))
            self.strength_bar.setStyleSheet(f"background: {color}; border-radius: 2px; border: none;")
            self._set_hint(self.strength_label, f"Password strength: {label}", color)
        self._validate_confirm_live(self.confirm_input.text())

    def _validate_confirm_live(self, text):
        if not text:
            self.confirm_hint.setText(""); return
        if text == self.password_input.text():
            self._set_hint(self.confirm_hint, "✓ Passwords match", "#00d4aa")
        else:
            self._set_hint(self.confirm_hint, "Passwords do not match", "#f76c6c")

    def _validate_all(self):
        u = self.username_input.text().strip()
        p = self.password_input.text()
        c = self.confirm_input.text()
        if not u: return "Username is required."
        if len(u) < 3: return "Username must be at least 3 characters."
        if not re.match(r"^[A-Za-z0-9_]+$", u): return "Username: only letters, numbers and underscores."
        if not p: return "Password is required."
        if len(p) < 6: return "Password must be at least 6 characters."
        if p != c: return "Passwords do not match."
        return None

    @pyqtSlot()
    def _on_register_clicked(self):
        err = self._validate_all()
        if err:
            self.error_label.setText(err); return
        self.error_label.setText("")
        self._set_loading(True)
        u = self.username_input.text().strip()
        p = self.password_input.text()
        self._worker = _RegisterWorker(u, p)
        self._worker.success.connect(lambda _: self._on_success(u, p))
        self._worker.failure.connect(self._on_failure)
        self._worker.start()

    def _on_success(self, username, password):
        self._set_loading(False)
        self.register_successful.emit(username, password)

    def _on_failure(self, message):
        self._set_loading(False)
        self.error_label.setText(message)

    def _set_loading(self, loading):
        self.register_btn.setEnabled(not loading)
        self.register_btn.setText("Creating account…" if loading else "Create Account")
        for w in (self.username_input, self.password_input, self.confirm_input):
            w.setEnabled(not loading)

    def reset(self):
        for w in (self.username_input, self.password_input, self.confirm_input):
            w.clear()
        for lbl in (self.username_hint, self.strength_label, self.confirm_hint, self.error_label):
            lbl.setText("")
        self.strength_bar.setFixedWidth(0)
        self._set_loading(False)