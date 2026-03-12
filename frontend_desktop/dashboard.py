"""
dashboard.py
------------
Main dashboard: upload CSV, view history, or logout.
"""

import os
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QFileDialog, QProgressBar,
    QSizePolicy, QDialog
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont, QDragEnterEvent, QDropEvent

import api
from session import Session


# ── Logout confirmation dialog ────────────────────────────────────────────────

class _LogoutDialog(QDialog):
    """Stylish custom logout confirmation popup."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.Dialog | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(360, 220)
        self._build_ui()

    def _build_ui(self):
        # ── Outer layout (sits on transparent window) ─────────────────────────
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        # ── Card ──────────────────────────────────────────────────────────────
        card = QFrame()
        card.setStyleSheet("""
            QFrame {
                background-color: #1a1f2e;
                border-radius: 18px;
                border: 1px solid #2a2f3e;
            }
        """)
        outer.addWidget(card)

        layout = QVBoxLayout(card)
        layout.setContentsMargins(36, 32, 36, 28)
        layout.setSpacing(0)

        # Icon
        icon = QLabel("🔒")
        icon.setAlignment(Qt.AlignCenter)
        icon.setFont(QFont("Segoe UI Emoji", 28))
        icon.setStyleSheet("border: none; background: transparent;")
        layout.addWidget(icon)

        layout.addSpacing(12)

        # Title
        title = QLabel("Log Out?")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Georgia", 16, QFont.Bold))
        title.setStyleSheet("color: #e8eaf0; border: none; background: transparent;")
        layout.addWidget(title)

        layout.addSpacing(8)

        # Subtitle
        subtitle = QLabel("Are you sure you want to log out?")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setWordWrap(True)
        subtitle.setStyleSheet("color: #6b7280; font-size: 12px; border: none; background: transparent;")
        layout.addWidget(subtitle)

        layout.addSpacing(28)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_row.setSpacing(12)

        no_btn = QPushButton("No, Stay")
        no_btn.setCursor(Qt.PointingHandCursor)
        no_btn.setFixedHeight(42)
        no_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        no_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #9ca3af;
                border: 1.5px solid #2a2f3e;
                border-radius: 10px;
            }
            QPushButton:hover {
                border-color: #00d4aa;
                color: #00d4aa;
                background: #00d4aa11;
            }
            QPushButton:pressed { background: #00d4aa22; }
        """)
        no_btn.clicked.connect(self.reject)

        yes_btn = QPushButton("Yes, Log Out")
        yes_btn.setCursor(Qt.PointingHandCursor)
        yes_btn.setFixedHeight(42)
        yes_btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        yes_btn.setStyleSheet("""
            QPushButton {
                background: #f76c6c22;
                color: #f76c6c;
                border: 1.5px solid #f76c6c;
                border-radius: 10px;
            }
            QPushButton:hover {
                background: #f76c6c44;
                color: #ff8f8f;
                border-color: #ff8f8f;
            }
            QPushButton:pressed { background: #f76c6c66; }
        """)
        yes_btn.clicked.connect(self.accept)

        btn_row.addWidget(no_btn)
        btn_row.addWidget(yes_btn)
        layout.addLayout(btn_row)


# ── Upload worker ─────────────────────────────────────────────────────────────

class _UploadWorker(QThread):
    success = pyqtSignal(dict)
    failure = pyqtSignal(str)

    def __init__(self, token: str, filepath: str):
        super().__init__()
        self._token    = token
        self._filepath = filepath

    def run(self):
        try:
            summary = api.upload_csv(self._token, self._filepath)
            self.success.emit(summary)
        except api.APIError as e:
            self.failure.emit(str(e))


# ── Dashboard widget ──────────────────────────────────────────────────────────

class DashboardWidget(QWidget):
    upload_complete   = pyqtSignal(dict, str)
    history_requested = pyqtSignal()
    logout_requested  = pyqtSignal()

    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self._worker = None
        self.setAcceptDrops(True)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget { background-color: #0e1117; color: #e8eaf0; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 36, 48, 36)
        outer.setSpacing(0)

        # ── Top bar ───────────────────────────────────────────────────────────
        top = QHBoxLayout()
        app_title = QLabel("⚗️  ChemEquip")
        app_title.setFont(QFont("Georgia", 14, QFont.Bold))
        app_title.setStyleSheet("color: #00d4aa;")

        self.user_label = QLabel("")
        self.user_label.setStyleSheet("color: #6b7280; font-size: 11px;")

        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.PointingHandCursor)
        logout_btn.setFixedSize(80, 32)
        logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1px solid #f76c6c44;
                border-radius: 7px;
                color: #f76c6c;
                font-size: 11px;
            }
            QPushButton:hover { background: #f76c6c22; }
        """)
        logout_btn.clicked.connect(self._confirm_logout)

        top.addWidget(app_title)
        top.addStretch()
        top.addWidget(self.user_label)
        top.addSpacing(12)
        top.addWidget(logout_btn)
        outer.addLayout(top)
        outer.addSpacing(40)

        # ── Welcome ───────────────────────────────────────────────────────────
        welcome = QLabel("Welcome back")
        welcome.setFont(QFont("Georgia", 26, QFont.Bold))
        welcome.setStyleSheet("color: #e8eaf0;")
        outer.addWidget(welcome)

        sub = QLabel("Upload a CSV dataset to analyse equipment parameters")
        sub.setStyleSheet("color: #6b7280; font-size: 13px;")
        outer.addWidget(sub)
        outer.addSpacing(40)

        # ── Drop zone ─────────────────────────────────────────────────────────
        self.drop_zone = QFrame()
        self.drop_zone.setMinimumHeight(200)
        self.drop_zone.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self._set_dropzone_idle()

        drop_layout = QVBoxLayout(self.drop_zone)
        drop_layout.setAlignment(Qt.AlignCenter)
        drop_layout.setSpacing(10)

        icon = QLabel("📂")
        icon.setFont(QFont("Segoe UI Emoji", 32))
        icon.setAlignment(Qt.AlignCenter)
        icon.setStyleSheet("border: none; background: transparent;")

        self.drop_label = QLabel("Drag & drop a CSV file here")
        self.drop_label.setAlignment(Qt.AlignCenter)
        self.drop_label.setFont(QFont("Segoe UI", 12))
        self.drop_label.setStyleSheet("color: #9ca3af; border: none; background: transparent;")

        or_label = QLabel("— or —")
        or_label.setAlignment(Qt.AlignCenter)
        or_label.setStyleSheet("color: #4b5563; font-size: 11px; border: none; background: transparent;")

        self.upload_btn = QPushButton("Browse File")
        self.upload_btn.setCursor(Qt.PointingHandCursor)
        self.upload_btn.setFixedSize(140, 40)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00d4aa, stop:1 #00a87d);
                color: #0e1117;
                border: none;
                border-radius: 9px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover  { background: #00e8bb; }
            QPushButton:pressed { background: #009e74; }
            QPushButton:disabled { background: #2a3040; color: #555; }
        """)
        self.upload_btn.clicked.connect(self._on_browse)

        drop_layout.addWidget(icon)
        drop_layout.addWidget(self.drop_label)
        drop_layout.addWidget(or_label)
        drop_layout.addWidget(self.upload_btn, alignment=Qt.AlignCenter)
        outer.addWidget(self.drop_zone)
        outer.addSpacing(16)

        # ── Progress / status ─────────────────────────────────────────────────
        self.status_label = QLabel("")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #9ca3af; font-size: 11px;")
        outer.addWidget(self.status_label)

        self.progress = QProgressBar()
        self.progress.setVisible(False)
        self.progress.setRange(0, 0)
        self.progress.setFixedHeight(4)
        self.progress.setStyleSheet("""
            QProgressBar { background: #1a1f2e; border: none; border-radius: 2px; }
            QProgressBar::chunk { background: #00d4aa; border-radius: 2px; }
        """)
        outer.addWidget(self.progress)
        outer.addSpacing(32)

        # ── Action row ────────────────────────────────────────────────────────
        actions = QHBoxLayout()
        actions.setSpacing(16)

        history_btn = self._action_card("🕒", "Upload History",
                                        "Browse your last 5 uploaded datasets", "#4f8ef7")
        history_btn.clicked.connect(self.history_requested.emit)
        actions.addWidget(history_btn)

        outer.addLayout(actions)
        outer.addStretch()

    def _action_card(self, icon, title, desc, accent):
        btn = QPushButton(f"{icon}  {title}")
        btn.setCursor(Qt.PointingHandCursor)
        btn.setMinimumHeight(70)
        btn.setFont(QFont("Segoe UI", 11, QFont.Bold))
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #1a1f2e;
                border: 1.5px solid #2a2f3e;
                border-radius: 12px;
                color: {accent};
                text-align: left;
                padding: 0 24px;
            }}
            QPushButton:hover {{ border-color: {accent}; background-color: #1e2537; }}
        """)
        return btn

    def _set_dropzone_idle(self):
        self.drop_zone.setStyleSheet("QFrame { border: 2px dashed #2a2f3e; border-radius: 16px; background-color: #111827; }")

    def _set_dropzone_active(self):
        self.drop_zone.setStyleSheet("QFrame { border: 2px dashed #00d4aa; border-radius: 16px; background-color: #00d4aa0d; }")

    def dragEnterEvent(self, event: QDragEnterEvent):
        if event.mimeData().hasUrls():
            if any(u.toLocalFile().endswith(".csv") for u in event.mimeData().urls()):
                self._set_dropzone_active()
                event.acceptProposedAction()

    def dragLeaveEvent(self, event):
        self._set_dropzone_idle()

    def dropEvent(self, event: QDropEvent):
        self._set_dropzone_idle()
        for url in event.mimeData().urls():
            path = url.toLocalFile()
            if path.endswith(".csv"):
                self._start_upload(path)
                break

    @pyqtSlot()
    def _on_browse(self):
        path, _ = QFileDialog.getOpenFileName(self, "Select CSV file", "", "CSV Files (*.csv)")
        if path:
            self._start_upload(path)

    def _start_upload(self, filepath: str):
        self._set_loading(True)
        fname = os.path.basename(filepath)
        self.status_label.setText(f'Uploading "{fname}"…')
        self._worker = _UploadWorker(self.session.token, filepath)
        self._worker.success.connect(lambda summary, f=fname: self._on_upload_success(summary, f))
        self._worker.failure.connect(self._on_upload_failure)
        self._worker.start()

    def _on_upload_success(self, summary: dict, filename: str):
        self._set_loading(False)
        self.status_label.setText("")
        self.upload_complete.emit(summary, f"Uploaded: {filename}")

    def _on_upload_failure(self, message: str):
        self._set_loading(False)
        self.status_label.setText(f"⚠  {message}")
        self.status_label.setStyleSheet("color: #f76c6c; font-size: 11px;")

    def _set_loading(self, loading: bool):
        self.upload_btn.setEnabled(not loading)
        self.progress.setVisible(loading)
        if not loading:
            self.status_label.setStyleSheet("color: #9ca3af; font-size: 11px;")

    # ── Logout confirmation ───────────────────────────────────────────────────

    def _confirm_logout(self):
        dialog = _LogoutDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            self.logout_requested.emit()

    # ── Public API ─────────────────────────────────────────────────────────────

    def refresh_user(self):
        if self.session.username:
            self.user_label.setText(f"Logged in as  {self.session.username}")