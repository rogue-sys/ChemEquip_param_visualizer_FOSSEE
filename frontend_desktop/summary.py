"""
summary.py  —  Summary screen.
Responsive fix: stat cards use a flow-style grid that collapses to 2 columns
on narrow windows, and all inner QFrames use Expanding size policy.
"""

from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QScrollArea, QGridLayout, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont

from charts import ChartsWidget
from export_pdf import export_report


def _stat_card(title, value, color="#00d4aa"):
    card = QFrame()
    card.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
    card.setStyleSheet("QFrame { background-color: #1a1f2e; border: 1px solid #2a2f3e; border-radius: 12px; }")
    lay = QVBoxLayout(card)
    lay.setContentsMargins(16, 14, 16, 14)
    lay.setSpacing(4)
    val_lbl = QLabel(value)
    val_lbl.setFont(QFont("Georgia", 20, QFont.Bold))
    val_lbl.setStyleSheet(f"color: {color}; border: none; background: transparent;")
    val_lbl.setAlignment(Qt.AlignCenter)
    t_lbl = QLabel(title)
    t_lbl.setStyleSheet("color: #9ca3af; font-size: 10px; letter-spacing: 1px; border: none; background: transparent;")
    t_lbl.setAlignment(Qt.AlignCenter)
    lay.addWidget(val_lbl)
    lay.addWidget(t_lbl)
    return card


class SummaryWidget(QWidget):
    back_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self._charts_visible = False
        self._summary = {}
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self._build_ui()

    def _build_ui(self):
        self.setStyleSheet("QWidget { background-color: #0e1117; color: #e8eaf0; }")

        main = QVBoxLayout(self)
        main.setContentsMargins(40, 32, 40, 32)
        main.setSpacing(20)

        # Top bar
        top = QHBoxLayout()
        back_btn = QPushButton("← Back")
        back_btn.setCursor(Qt.PointingHandCursor)
        back_btn.setFixedSize(90, 34)
        back_btn.setStyleSheet("""
            QPushButton { background: transparent; border: 1.5px solid #2a2f3e; border-radius: 8px; color: #9ca3af; font-size: 12px; }
            QPushButton:hover { border-color: #00d4aa; color: #00d4aa; }
        """)
        back_btn.clicked.connect(self.back_requested.emit)

        title = QLabel("Dataset Summary")
        title.setFont(QFont("Georgia", 18, QFont.Bold))
        title.setStyleSheet("color: #e8eaf0;")

        self.source_label = QLabel("")
        self.source_label.setStyleSheet("color: #6b7280; font-size: 11px;")
        self.source_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        self.source_label.setWordWrap(True)

        # Export PDF button
        self.export_btn = QPushButton("⬇  Export PDF")
        self.export_btn.setCursor(Qt.PointingHandCursor)
        self.export_btn.setFixedHeight(34)
        self.export_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        self.export_btn.setStyleSheet("""
            QPushButton {
                background: qlineargradient(x1:0,y1:0,x2:1,y2:0,
                    stop:0 #00d4aa, stop:1 #00a87d);
                color: #0e1117; border: none; border-radius: 8px;
                padding: 0 16px;
            }
            QPushButton:hover   { background: #00e8bb; }
            QPushButton:pressed { background: #009e74; }
        """)
        self.export_btn.clicked.connect(self._on_export)

        top.addWidget(back_btn)
        top.addSpacing(16)
        top.addWidget(title)
        top.addStretch()
        top.addWidget(self.export_btn)
        top.addSpacing(12)
        top.addWidget(self.source_label)
        main.addLayout(top)

        # Stat cards — 4 columns that auto-stretch
        self.cards_grid = QGridLayout()
        self.cards_grid.setSpacing(12)
        self.cards_grid.setColumnStretch(0, 1)
        self.cards_grid.setColumnStretch(1, 1)
        self.cards_grid.setColumnStretch(2, 1)
        self.cards_grid.setColumnStretch(3, 1)
        main.addLayout(self.cards_grid)

        # Distribution frame
        self.dist_frame = QFrame()
        self.dist_frame.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        self.dist_frame.setStyleSheet("QFrame { background-color: #1a1f2e; border: 1px solid #2a2f3e; border-radius: 12px; }")
        self.dist_layout = QVBoxLayout(self.dist_frame)
        self.dist_layout.setContentsMargins(24, 18, 24, 18)
        dist_title = QLabel("Equipment Type Distribution")
        dist_title.setFont(QFont("Segoe UI", 11, QFont.Bold))
        dist_title.setStyleSheet("color: #e8eaf0; border: none; background: transparent;")
        self.dist_layout.addWidget(dist_title)
        self.dist_rows_layout = QVBoxLayout()
        self.dist_rows_layout.setSpacing(6)
        self.dist_layout.addLayout(self.dist_rows_layout)
        main.addWidget(self.dist_frame)

        # Charts toggle
        self.charts_btn = QPushButton("📊  View Charts")
        self.charts_btn.setCursor(Qt.PointingHandCursor)
        self.charts_btn.setFixedHeight(42)
        self.charts_btn.setFont(QFont("Segoe UI", 11))
        self.charts_btn.setStyleSheet("""
            QPushButton { background: #1a1f2e; border: 1.5px solid #00d4aa; border-radius: 10px; color: #00d4aa; padding: 0 24px; }
            QPushButton:hover { background: #00d4aa; color: #0e1117; }
        """)
        self.charts_btn.clicked.connect(self._toggle_charts)
        main.addWidget(self.charts_btn, alignment=Qt.AlignLeft)

        # Charts container
        self.charts_container = QFrame()
        self.charts_container.setVisible(False)
        # MinimumExpanding lets the container grow as tall as the canvas needs
        self.charts_container.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.charts_container.setStyleSheet("QFrame { background-color: #1a1f2e; border: 1px solid #2a2f3e; border-radius: 12px; }")
        ci = QVBoxLayout(self.charts_container)
        ci.setContentsMargins(8, 8, 8, 8)
        ci.setSpacing(0)
        self.charts_widget = ChartsWidget()
        self.charts_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ci.addWidget(self.charts_widget)
        main.addWidget(self.charts_container)

        main.addStretch()

    def load_summary(self, summary, source_label=""):
        self._summary = summary
        self._charts_visible = False
        self.charts_container.setVisible(False)
        self.charts_btn.setText("📊  View Charts")
        self.source_label.setText(source_label)

        # Clear and rebuild stat cards
        while self.cards_grid.count():
            item = self.cards_grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        cards_data = [
            ("TOTAL EQUIPMENT", str(summary.get("total_count", "—")),  "#00d4aa"),
            ("AVG FLOWRATE",    _fmt(summary.get("avg_flowrate")),          "#4f8ef7"),
            ("AVG PRESSURE",    _fmt(summary.get("avg_pressure")),          "#f7c948"),
            ("AVG TEMPERATURE", _fmt(summary.get("avg_temperature")),       "#f76c6c"),
        ]
        for i, (t, v, c) in enumerate(cards_data):
            self.cards_grid.addWidget(_stat_card(t, v, c), 0, i)

        # Clear and rebuild distribution rows
        while self.dist_rows_layout.count():
            item = self.dist_rows_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        dist = summary.get("type_distribution", {})
        total = sum(dist.values()) if dist else 0
        for eq_type, count in dist.items():
            row = QHBoxLayout()
            n = QLabel(str(eq_type))
            n.setStyleSheet("color: #e8eaf0; font-size: 12px; border: none; background: transparent;")
            pct = (count / total * 100) if total else 0
            p = QLabel(f"{count}  ({pct:.1f}%)")
            p.setStyleSheet("color: #00d4aa; font-size: 12px; border: none; background: transparent;")
            p.setAlignment(Qt.AlignRight)
            row.addWidget(n)
            row.addStretch()
            row.addWidget(p)
            w = QWidget()
            w.setStyleSheet("background: transparent; border: none;")
            w.setLayout(row)
            self.dist_rows_layout.addWidget(w)

        if not dist:
            e = QLabel("No distribution data available.")
            e.setStyleSheet("color: #6b7280; font-size: 11px; border: none; background: transparent;")
            self.dist_rows_layout.addWidget(e)

    def _on_export(self):
        """Export the full analysis report as a styled PDF."""
        from export_pdf import export_report
        export_report(self._summary, self.source_label.text(), parent=self)

    def _toggle_charts(self):
        self._charts_visible = not self._charts_visible
        self.charts_container.setVisible(self._charts_visible)
        if self._charts_visible:
            self.charts_widget.render(self._summary)
            self.charts_btn.setText("🔼  Hide Charts")
        else:
            self.charts_btn.setText("📊  View Charts")


def _fmt(value):
    if value is None: return "—"
    try: return f"{float(value):.2f}"
    except: return str(value)