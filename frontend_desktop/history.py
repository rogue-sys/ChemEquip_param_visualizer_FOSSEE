"""
history.py
----------
History screen: fetches last 5 uploads and lets the user click into any one
to view its summary.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QThread, pyqtSlot
from PyQt5.QtGui import QFont

import api
from session import Session


# ── Background worker ─────────────────────────────────────────────────────────

class _HistoryWorker(QThread):
    success = pyqtSignal(list)
    failure = pyqtSignal(str)

    def __init__(self, token: str):
        super().__init__()
        self._token = token

    def run(self):
        try:
            records = api.get_history(self._token)
            self.success.emit(records)
        except api.APIError as e:
            self.failure.emit(str(e))


# ── History item card ─────────────────────────────────────────────────────────

class _HistoryItem(QFrame):
    """Clickable card for a single history record."""

    clicked = pyqtSignal(dict)   # emits the summary dict

    def __init__(self, record: dict, index: int, parent=None):
        super().__init__(parent)
        self._summary = record.get("summary", {})
        self._build_ui(record, index)
        self.setCursor(Qt.PointingHandCursor)

    def _build_ui(self, record: dict, index: int):
        self.setStyleSheet("""
            QFrame {
                background-color: #1a1f2e;
                border: 1px solid #2a2f3e;
                border-radius: 12px;
            }
            QFrame:hover {
                border-color: #00d4aa;
                background-color: #1e2537;
            }
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)

        # Index badge
        badge = QLabel(str(index))
        badge.setFixedSize(32, 32)
        badge.setAlignment(Qt.AlignCenter)
        badge.setFont(QFont("Georgia", 12, QFont.Bold))
        badge.setStyleSheet("""
            background-color: #00d4aa22;
            color: #00d4aa;
            border-radius: 16px;
            border: 1px solid #00d4aa44;
        """)
        layout.addWidget(badge)
        layout.addSpacing(14)

        # File info
        info = QVBoxLayout()
        info.setSpacing(2)

        fname = QLabel(record.get("filename", "Unknown file"))
        fname.setFont(QFont("Segoe UI", 11, QFont.Bold))
        fname.setStyleSheet("color: #e8eaf0; border: none; background: transparent;")

        date_str = record.get("uploaded_at", "")
        if date_str:
            try:
                # e.g. "2024-06-10T14:32:00Z" → "2024-06-10 14:32"
                date_str = date_str[:16].replace("T", "  ")
            except Exception:
                pass
        date_lbl = QLabel(date_str)
        date_lbl.setStyleSheet("color: #6b7280; font-size: 10px; border: none; background: transparent;")

        info.addWidget(fname)
        info.addWidget(date_lbl)
        layout.addLayout(info)
        layout.addStretch()

        summary = record.get("summary", {})
        eq_count = summary.get("total_count", "—")
        meta_lbl = QLabel(f"{eq_count} items")
        meta_lbl.setStyleSheet("color: #4f8ef7; font-size: 11px; border: none; background: transparent;")
        layout.addWidget(meta_lbl)

        arrow = QLabel("›")
        arrow.setFont(QFont("Segoe UI", 18))
        arrow.setStyleSheet("color: #2a2f3e; border: none; background: transparent; margin-left: 8px;")
        layout.addWidget(arrow)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit(self._summary)
        super().mousePressEvent(event)


# ── History widget ────────────────────────────────────────────────────────────

class HistoryWidget(QWidget):
    """
    History screen.
    Emits:
      back_requested        — user clicked Back
      view_summary(dict)    — user clicked a history item
    """

    back_requested = pyqtSignal()
    view_summary   = pyqtSignal(dict, str)   # (summary_dict, source_label)

    def __init__(self, session: Session, parent=None):
        super().__init__(parent)
        self.session = session
        self._worker = None
        self._build_ui()

    # ── UI construction ────────────────────────────────────────────────────────

    def _build_ui(self):
        self.setStyleSheet("QWidget { background-color: #0e1117; color: #e8eaf0; }")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(48, 36, 48, 36)
        outer.setSpacing(24)

        # ── Top bar ───────────────────────────────────────────────────────────
        top = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedSize(90, 34)
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                border: 1.5px solid #2a2f3e;
                border-radius: 8px;
                color: #9ca3af;
                font-size: 12px;
            }
            QPushButton:hover { border-color: #00d4aa; color: #00d4aa; }
        """)
        back_btn.clicked.connect(self.back_requested.emit)

        title = QLabel("Upload History")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #e8eaf0;")

        top.addWidget(back_btn)
        top.addSpacing(16)
        top.addWidget(title)
        top.addStretch()
        outer.addLayout(top)

        # ── Status / error label ──────────────────────────────────────────────
        self.status_label = QLabel("Loading…")
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setStyleSheet("color: #9ca3af; font-size: 12px;")
        outer.addWidget(self.status_label)

        # ── Scroll area for history items ─────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        outer.addWidget(scroll)

        self.list_container = QWidget()
        self.list_container.setStyleSheet("background: transparent;")
        self.list_layout = QVBoxLayout(self.list_container)
        self.list_layout.setContentsMargins(0, 0, 0, 0)
        self.list_layout.setSpacing(10)
        self.list_layout.addStretch()
        scroll.setWidget(self.list_container)

    # ── Public API ─────────────────────────────────────────────────────────────

    def refresh(self):
        """Trigger a fresh history fetch from the backend."""
        self.status_label.setText("Loading…")
        self.status_label.setVisible(True)
        self._clear_list()

        self._worker = _HistoryWorker(self.session.token)
        self._worker.success.connect(self._on_loaded)
        self._worker.failure.connect(self._on_error)
        self._worker.start()

    # ── Slots ──────────────────────────────────────────────────────────────────

    @pyqtSlot(list)
    def _on_loaded(self, records: list):
        self.status_label.setVisible(False)
        self._clear_list()

        if not records:
            self.status_label.setText("No uploads yet.")
            self.status_label.setVisible(True)
            return

        for idx, record in enumerate(records, start=1):
            item = _HistoryItem(record, idx)
            item.clicked.connect(
                lambda summary, r=record: self.view_summary.emit(
                    summary,
                    f"From history: {r.get('filename', '')}  •  {r.get('uploaded_at', '')[:10]}"
                )
            )
            self.list_layout.insertWidget(self.list_layout.count() - 1, item)

    @pyqtSlot(str)
    def _on_error(self, message: str):
        self.status_label.setText(f"⚠  {message}")
        self.status_label.setStyleSheet("color: #f76c6c; font-size: 12px;")

    def _clear_list(self):
        # Remove all items except the trailing stretch
        while self.list_layout.count() > 1:
            item = self.list_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
