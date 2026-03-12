"""
charts.py
---------
Enhanced embedded Matplotlib charts for PyQt5.
4 rich charts in a 2x2 grid:
  1. Horizontal bar  — Equipment type distribution (gradient + % labels)
  2. Donut/pie       — Equipment type share
  3. Radial gauge    — Average metrics as filled arc gauges
  4. Grouped bars    — Min / Avg / Max metrics comparison (if available)
     Falls back to styled single-value bars when min/max not in summary.
"""

import math
import numpy as np
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import FancyArrowPatch, Arc, Wedge
import matplotlib.patches as mpatches
import matplotlib.patheffects as pe

# ── Palette ───────────────────────────────────────────────────────────────────
BG      = "#0e1117"
SURFACE = "#161b27"
CARD    = "#1a1f2e"
BORDER  = "#2a2f3e"
TEXT    = "#e8eaf0"
SUBTEXT = "#6b7280"
COLORS  = ["#00d4aa", "#4f8ef7", "#f7c948", "#f76c6c", "#c97ef7", "#6cf7c0", "#f7956c"]
METRIC_COLORS = {
    "avg_flowrate":    "#4f8ef7",
    "avg_pressure":    "#f7c948",
    "avg_temperature": "#f76c6c",
}


# ── Shared axis styler ────────────────────────────────────────────────────────

def _style(ax, title="", xlabel="", ylabel="", grid_axis="x"):
    ax.set_facecolor(SURFACE)
    if title:
        ax.set_title(title, color=TEXT, fontsize=10, fontweight="bold",
                     pad=12, loc="left")
    if xlabel:
        ax.set_xlabel(xlabel, color=SUBTEXT, fontsize=8, labelpad=6)
    if ylabel:
        ax.set_ylabel(ylabel, color=SUBTEXT, fontsize=8, labelpad=6)
    ax.tick_params(colors=SUBTEXT, labelsize=8, length=3)
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)
        spine.set_linewidth(0.8)
    if grid_axis == "x":
        ax.xaxis.grid(True, color=BORDER, linestyle="--", linewidth=0.5, alpha=0.7)
        ax.yaxis.grid(False)
    elif grid_axis == "y":
        ax.yaxis.grid(True, color=BORDER, linestyle="--", linewidth=0.5, alpha=0.7)
        ax.xaxis.grid(False)
    elif grid_axis == "both":
        ax.grid(True, color=BORDER, linestyle="--", linewidth=0.5, alpha=0.7)
    else:
        ax.grid(False)
    ax.set_axisbelow(True)


def _no_data(ax, msg="No data available"):
    ax.set_facecolor(SURFACE)
    ax.text(0.5, 0.5, msg, ha="center", va="center",
            color=SUBTEXT, fontsize=9, transform=ax.transAxes)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_edgecolor(BORDER)


# ── Chart 1: Horizontal bar — distribution ────────────────────────────────────

def draw_distribution_bar(ax, summary):
    dist = summary.get("type_distribution", {})
    if not dist:
        _no_data(ax, "No distribution data"); return

    labels = list(dist.keys())
    values = list(dist.values())
    total  = sum(values)
    n      = len(labels)
    y_pos  = np.arange(n)

    # Draw background track
    ax.barh(y_pos, [max(values) * 1.15] * n,
            color=BORDER, height=0.55, zorder=1, alpha=0.35)

    # Draw value bars with per-bar colour
    for i, (y, v) in enumerate(zip(y_pos, values)):
        color = COLORS[i % len(COLORS)]
        ax.barh(y, v, color=color, height=0.55, zorder=3,
                linewidth=0, alpha=0.92)

        pct = v / total * 100 if total else 0
        # Value inside bar (if wide enough) else outside
        if v / max(values) > 0.35:
            ax.text(v - max(values) * 0.02, y, f"{v}  ({pct:.1f}%)",
                    va="center", ha="right", color=BG,
                    fontsize=8, fontweight="bold", zorder=5)
        else:
            ax.text(v + max(values) * 0.02, y, f"{v}  ({pct:.1f}%)",
                    va="center", ha="left", color=TEXT,
                    fontsize=8, zorder=5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=TEXT, fontsize=9)
    ax.set_xlim(0, max(values) * 1.25)
    ax.xaxis.set_visible(False)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_facecolor(SURFACE)
    ax.set_title("Equipment Distribution", color=TEXT,
                 fontsize=10, fontweight="bold", pad=10, loc="left")
    ax.invert_yaxis()


# ── Chart 2: Donut chart — equipment share ────────────────────────────────────

def draw_donut(ax, summary):
    dist = summary.get("type_distribution", {})
    if not dist:
        _no_data(ax, "No distribution data"); return

    labels = list(dist.keys())
    values = list(dist.values())
    colors = [COLORS[i % len(COLORS)] for i in range(len(labels))]
    total  = sum(values)

    wedge_props = dict(width=0.45, edgecolor=BG, linewidth=2)
    wedges, _ = ax.pie(
        values, colors=colors, startangle=90,
        wedgeprops=wedge_props, counterclock=False
    )

    # Hover-style: slight explode on largest slice
    max_idx = values.index(max(values))
    wedges[max_idx].set_radius(1.08)

    # Centre label
    ax.text(0, 0, f"{total}\ntotal", ha="center", va="center",
            color=TEXT, fontsize=11, fontweight="bold",
            linespacing=1.5)

    # Legend outside
    legend_labels = [f"{l}  ({v/total*100:.1f}%)" for l, v in zip(labels, values)]
    ax.legend(wedges, legend_labels,
              loc="lower center", bbox_to_anchor=(0.5, -0.22),
              ncol=min(3, len(labels)),
              fontsize=7, frameon=False,
              labelcolor=TEXT, handlelength=1.2, handleheight=0.8)

    ax.set_facecolor(SURFACE)
    ax.set_title("Equipment Share", color=TEXT,
                 fontsize=10, fontweight="bold", pad=10, loc="left")


# ── Chart 3: Arc gauges — average metrics ─────────────────────────────────────

def draw_gauges(ax, summary):
    """Draw 3 semi-circle arc gauges side by side inside one axes."""
    metrics = {
        "Flowrate":    ("avg_flowrate",    "#4f8ef7"),
        "Pressure":    ("avg_pressure",    "#f7c948"),
        "Temperature": ("avg_temperature", "#f76c6c"),
    }

    ax.set_xlim(0, 3)
    ax.set_ylim(-0.6, 1.3)
    ax.set_aspect("equal")
    ax.set_facecolor(SURFACE)
    ax.set_xticks([]); ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.set_title("Average Metrics — Gauges", color=TEXT,
                 fontsize=10, fontweight="bold", pad=10, loc="left")

    # Collect all values to normalise arcs relative to max
    raw = {}
    for label, (key, _) in metrics.items():
        v = summary.get(key)
        try:
            raw[label] = float(v) if v is not None else 0.0
        except (TypeError, ValueError):
            raw[label] = 0.0

    max_val = max(raw.values()) if raw.values() else 1
    if max_val == 0:
        max_val = 1

    for idx, (label, (key, color)) in enumerate(metrics.items()):
        cx = idx + 0.5
        cy = 0.35
        r_outer = 0.38
        r_inner = 0.24

        val     = raw[label]
        pct     = val / max_val
        angle   = pct * 180          # 0–180 degrees

        # Background arc (full 180°)
        bg = Wedge((cx, cy), r_outer, 0, 180,
                   width=r_outer - r_inner,
                   facecolor=BORDER, edgecolor="none", zorder=2)
        ax.add_patch(bg)

        # Value arc
        if angle > 0:
            fg = Wedge((cx, cy), r_outer, 180 - angle, 180,
                       width=r_outer - r_inner,
                       facecolor=color, edgecolor="none",
                       zorder=3, alpha=0.92)
            ax.add_patch(fg)

            # Glow tip dot
            tip_rad = math.radians(180 - angle)
            tip_x = cx + (r_outer - (r_outer - r_inner) / 2) * math.cos(tip_rad)
            tip_y = cy + (r_outer - (r_outer - r_inner) / 2) * math.sin(tip_rad)
            ax.plot(tip_x, tip_y, "o", color=color,
                    markersize=5, zorder=5,
                    markeredgecolor=BG, markeredgewidth=1)

        # Centre value text
        ax.text(cx, cy - 0.04, f"{val:.1f}",
                ha="center", va="center", color=TEXT,
                fontsize=9, fontweight="bold", zorder=6)

        # Label below
        ax.text(cx, cy - 0.28, label,
                ha="center", va="top", color=SUBTEXT,
                fontsize=7.5, zorder=6)

        # % of max below label
        ax.text(cx, cy - 0.42, f"{pct*100:.0f}% of max",
                ha="center", va="top", color=color,
                fontsize=7, zorder=6)


# ── Chart 4: Styled vertical bars — metrics comparison ───────────────────────

def draw_metrics_bar(ax, summary):
    metric_keys = {
        "avg_flowrate":    ("Flowrate",    "#4f8ef7"),
        "avg_pressure":    ("Pressure",    "#f7c948"),
        "avg_temperature": ("Temperature", "#f76c6c"),
    }

    labels, values, colors = [], [], []
    for key, (label, color) in metric_keys.items():
        v = summary.get(key)
        try:
            val = float(v) if v is not None else None
        except (TypeError, ValueError):
            val = None
        if val is not None:
            labels.append(label)
            values.append(val)
            colors.append(color)

    if not values:
        _no_data(ax, "No metric data"); return

    x = np.arange(len(labels))
    max_v = max(values)

    # Shadow bars (background height reference)
    ax.bar(x, [max_v * 1.12] * len(values),
           color=BORDER, width=0.5, zorder=1, alpha=0.3)

    # Main bars
    bars = ax.bar(x, values, color=colors, width=0.5,
                  zorder=3, linewidth=0, alpha=0.9)

    # Gradient effect: lighter top strip
    for bar, color in zip(bars, colors):
        h = bar.get_height()
        ax.bar(bar.get_x(), h * 0.18, bottom=h * 0.82,
               width=bar.get_width(), color="white",
               alpha=0.12, zorder=4, linewidth=0)

    # Value labels on top
    for bar, val, color in zip(bars, values, colors):
        ax.text(bar.get_x() + bar.get_width() / 2,
                bar.get_height() + max_v * 0.025,
                f"{val:.2f}",
                ha="center", va="bottom", color=color,
                fontsize=9, fontweight="bold", zorder=5)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=TEXT, fontsize=9, fontweight="bold")
    ax.set_ylim(0, max_v * 1.22)
    ax.yaxis.set_visible(False)

    _style(ax, title="Average Metrics", grid_axis="none")
    # Remove top/right spines for cleaner look
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)


# ── Main widget ───────────────────────────────────────────────────────────────

class ChartsWidget(QWidget):
    """
    2×2 grid of rich dark-theme charts.
    Call render(summary) to draw/refresh.
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        self.figure = Figure(figsize=(13, 8), facecolor=BG)
        self.figure.subplots_adjust(
            left=0.07, right=0.97,
            top=0.93, bottom=0.12,
            wspace=0.32, hspace=0.48
        )
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setStyleSheet(f"background-color: {BG};")
        # ── KEY: enforce a minimum height so the 2x2 grid is never squashed ──
        self.canvas.setMinimumHeight(620)
        from PyQt5.QtWidgets import QSizePolicy
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.canvas)

    def render(self, summary: dict):
        self.figure.clear()

        ax1 = self.figure.add_subplot(2, 2, 1)   # top-left:  distribution bar
        ax2 = self.figure.add_subplot(2, 2, 2)   # top-right: donut
        ax3 = self.figure.add_subplot(2, 2, 3)   # bot-left:  gauges
        ax4 = self.figure.add_subplot(2, 2, 4)   # bot-right: metrics bar

        draw_distribution_bar(ax1, summary)
        draw_donut(ax2, summary)
        draw_gauges(ax3, summary)
        draw_metrics_bar(ax4, summary)

        # Section divider line between rows
        self.figure.add_artist(
            mpatches.FancyArrowPatch(
                (0.03, 0.505), (0.97, 0.505),
                arrowstyle="-",
                color=BORDER, linewidth=0.8,
                transform=self.figure.transFigure,
                figure=self.figure
            )
        )

        self.canvas.draw()