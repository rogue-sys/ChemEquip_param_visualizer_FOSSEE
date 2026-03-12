"""
main.py
-------
Application entry point.
Uses QStackedWidget to swap between Login, Register, Dashboard, Summary,
and History without ever destroying widgets.

Scroll + responsive layout fix:
- Every page is wrapped in a QScrollArea with widgetResizable=True
- The scroll area background matches the app theme
- SizePolicy on every page widget is set to Preferred/Expanding so Qt can
  freely resize them — no widget blocks the layout negotiation
"""

import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QStackedWidget,
    QScrollArea, QWidget, QSizePolicy
)
from PyQt5.QtCore import Qt

from session import Session
from login import LoginWidget
from register import RegisterWidget
from dashboard import DashboardWidget
from summary import SummaryWidget
from history import HistoryWidget


# ── Page index constants ──────────────────────────────────────────────────────
PAGE_LOGIN     = 0
PAGE_DASHBOARD = 1
PAGE_SUMMARY   = 2
PAGE_HISTORY   = 3
PAGE_REGISTER  = 4


# ── Scroll wrapper ────────────────────────────────────────────────────────────

def _scrollable(widget: QWidget) -> QScrollArea:
    """
    Wraps a page widget in a properly configured QScrollArea.

    Key settings that fix both the scroll and resize problems:
      - widgetResizable=True   : inner widget resizes with the scroll area
      - HorizontalScrollBar=AlwaysOff : no horizontal bar ever
      - VerticalScrollBar=AsNeeded    : vertical bar only when overflowing
      - The widget itself gets an Expanding size policy so it fills space
        when the window is large, but scrolls when the window is small
    """
    # Let the page widget grow/shrink freely with the window
    widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    scroll = QScrollArea()
    scroll.setWidget(widget)
    scroll.setWidgetResizable(True)
    scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
    scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
    scroll.setFrameShape(QScrollArea.NoFrame)
    scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
    scroll.setStyleSheet("""
        QScrollArea {
            background-color: #0e1117;
            border: none;
        }
        QWidget#qt_scrollarea_viewport {
            background-color: #0e1117;
        }
        QScrollBar:vertical {
            background: #1a1f2e;
            width: 8px;
            border-radius: 4px;
            margin: 0;
        }
        QScrollBar::handle:vertical {
            background: #2a2f3e;
            border-radius: 4px;
            min-height: 30px;
        }
        QScrollBar::handle:vertical:hover {
            background: #00d4aa;
        }
        QScrollBar::add-line:vertical,
        QScrollBar::sub-line:vertical {
            height: 0px;
        }
    """)
    # Ensure the viewport (the visible area inside the scroll) also gets
    # the right background — avoids white flashes on resize
    scroll.viewport().setStyleSheet("background-color: #0e1117;")
    return scroll


# ── Main window ───────────────────────────────────────────────────────────────

class MainWindow(QMainWindow):
    """
    Root window. Owns a QStackedWidget and the shared Session object.
    All navigation is handled here so child widgets stay decoupled.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Parameter Visualizer")
        self.setMinimumSize(480, 400)   # allow small windows — scroll handles the rest
        self.resize(1100, 720)
        self.setStyleSheet("QMainWindow { background-color: #0e1117; }")

        # ── Shared session ────────────────────────────────────────────────────
        self.session = Session()

        # ── Stacked widget ────────────────────────────────────────────────────
        self.stack = QStackedWidget()
        self.stack.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.stack)

        # ── Screens ───────────────────────────────────────────────────────────
        self.login_widget     = LoginWidget(self.session)
        self.dashboard_widget = DashboardWidget(self.session)
        self.summary_widget   = SummaryWidget()
        self.history_widget   = HistoryWidget(self.session)
        self.register_widget  = RegisterWidget()

        self.stack.addWidget(_scrollable(self.login_widget))      # PAGE_LOGIN     = 0
        self.stack.addWidget(_scrollable(self.dashboard_widget))  # PAGE_DASHBOARD = 1
        self.stack.addWidget(_scrollable(self.summary_widget))    # PAGE_SUMMARY   = 2
        self.stack.addWidget(_scrollable(self.history_widget))    # PAGE_HISTORY   = 3
        self.stack.addWidget(_scrollable(self.register_widget))   # PAGE_REGISTER  = 4

        # ── Wire signals ──────────────────────────────────────────────────────
        self.login_widget.login_successful.connect(self._on_login)
        self.login_widget.register_requested.connect(self._show_register)

        self.register_widget.back_to_login.connect(self._show_login)
        self.register_widget.register_successful.connect(self._on_register_success)

        self.dashboard_widget.upload_complete.connect(self._show_summary)
        self.dashboard_widget.history_requested.connect(self._show_history)
        self.dashboard_widget.logout_requested.connect(self._on_logout)

        self.summary_widget.back_requested.connect(lambda: self._go_to(PAGE_DASHBOARD))
        self.history_widget.back_requested.connect(lambda: self._go_to(PAGE_DASHBOARD))
        self.history_widget.view_summary.connect(self._show_summary)

        self.stack.setCurrentIndex(PAGE_LOGIN)

    # ── Navigation ────────────────────────────────────────────────────────────

    def _go_to(self, page: int):
        self.stack.setCurrentIndex(page)

    def _show_login(self):
        self.login_widget.reset()
        self._go_to(PAGE_LOGIN)

    def _show_register(self):
        self.register_widget.reset()
        self._go_to(PAGE_REGISTER)

    def _on_login(self, token: str, username: str):
        self.dashboard_widget.refresh_user()
        self._go_to(PAGE_DASHBOARD)

    def _on_register_success(self, username: str, password: str):
        self.register_widget.reset()
        self.login_widget.username_input.setText(username)
        self.login_widget.password_input.setText(password)
        self.login_widget._on_login_clicked()

    def _show_summary(self, summary: dict, source_label: str = ""):
        self.summary_widget.load_summary(summary, source_label)
        self._go_to(PAGE_SUMMARY)

    def _show_history(self):
        self.history_widget.refresh()
        self._go_to(PAGE_HISTORY)

    def _on_logout(self):
        self.session.logout()
        self.login_widget.reset()
        self._go_to(PAGE_LOGIN)


# ── Entry point ───────────────────────────────────────────────────────────────

def main():
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    app = QApplication(sys.argv)
    app.setApplicationName("Chemical Equipment Parameter Visualizer")
    app.setStyle("Fusion")

    window = MainWindow()
    window.show()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()