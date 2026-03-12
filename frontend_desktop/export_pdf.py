"""
export_pdf.py
-------------
Generates a styled PDF report from the analysis summary + charts.
Uses only matplotlib (already a dependency) — no extra libraries needed.

Call:  export_report(summary, source_label, parent_widget)
"""

import io
import os
import datetime
from PyQt5.QtWidgets import QFileDialog, QMessageBox
import matplotlib
matplotlib.use("Agg")   # off-screen rendering for PDF
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.patches import FancyBboxPatch, Wedge
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import math

# ── Palette (matches app theme) ───────────────────────────────────────────────
BG      = "#0e1117"
SURFACE = "#1a1f2e"
BORDER  = "#2a2f3e"
TEXT    = "#e8eaf0"
SUBTEXT = "#6b7280"
ACCENT  = "#00d4aa"
COLORS  = ["#00d4aa", "#4f8ef7", "#f7c948", "#f76c6c", "#c97ef7", "#6cf7c0", "#f7956c"]
METRIC_COLORS = ["#4f8ef7", "#f7c948", "#f76c6c"]


# ── Helpers ───────────────────────────────────────────────────────────────────

def _fmt(v):
    if v is None: return "—"
    try:    return f"{float(v):.2f}"
    except: return str(v)


def _style_ax(ax, title="", grid="x"):
    ax.set_facecolor(SURFACE)
    if title:
        ax.set_title(title, color=TEXT, fontsize=9, fontweight="bold",
                     pad=8, loc="left")
    ax.tick_params(colors=SUBTEXT, labelsize=7, length=2)
    for sp in ax.spines.values():
        sp.set_edgecolor(BORDER); sp.set_linewidth(0.6)
    if grid == "x":
        ax.xaxis.grid(True, color=BORDER, linestyle="--", lw=0.4, alpha=0.7)
        ax.yaxis.grid(False)
    elif grid == "y":
        ax.yaxis.grid(True, color=BORDER, linestyle="--", lw=0.4, alpha=0.7)
        ax.xaxis.grid(False)
    ax.set_axisbelow(True)


# ── Page 1: Cover + stats table ───────────────────────────────────────────────

def _draw_cover(fig, summary, source_label):
    fig.patch.set_facecolor(BG)
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_facecolor(BG)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.axis("off")

    # Top accent bar
    ax.add_patch(FancyBboxPatch((0, 0.91), 1, 0.09,
        boxstyle="square,pad=0", facecolor=SURFACE, edgecolor=BORDER, lw=0.5))
    ax.add_patch(FancyBboxPatch((0, 0.91), 0.006, 0.09,
        boxstyle="square,pad=0", facecolor=ACCENT, edgecolor="none"))

    # Title
    ax.text(0.04, 0.955, "⚗  Chemical Equipment Parameter Visualizer",
            color=ACCENT, fontsize=14, fontweight="bold", va="center")
    ax.text(0.04, 0.935, "Analysis Report",
            color=SUBTEXT, fontsize=9, va="center")

    # Date / source
    now = datetime.datetime.now().strftime("%B %d, %Y  %H:%M")
    ax.text(0.96, 0.955, now, color=SUBTEXT, fontsize=8,
            ha="right", va="center")
    if source_label:
        ax.text(0.96, 0.935, source_label, color=SUBTEXT, fontsize=7,
                ha="right", va="center")

    # ── Stats summary box ─────────────────────────────────────────────────────
    ax.add_patch(FancyBboxPatch((0.04, 0.72), 0.92, 0.16,
        boxstyle="round,pad=0.01", facecolor=SURFACE,
        edgecolor=BORDER, lw=0.6))

    stats = [
        ("TOTAL EQUIPMENT",  str(summary.get("total_count", "—")),  ACCENT),
        ("AVG FLOWRATE",     _fmt(summary.get("avg_flowrate")),      "#4f8ef7"),
        ("AVG PRESSURE",     _fmt(summary.get("avg_pressure")),      "#f7c948"),
        ("AVG TEMPERATURE",  _fmt(summary.get("avg_temperature")),   "#f76c6c"),
    ]
    col_w = 0.92 / len(stats)
    for i, (label, value, color) in enumerate(stats):
        cx = 0.04 + col_w * i + col_w / 2
        ax.text(cx, 0.845, value, color=color, fontsize=18,
                fontweight="bold", ha="center", va="center")
        ax.text(cx, 0.742, label, color=SUBTEXT, fontsize=6.5,
                ha="center", va="center", fontfamily="monospace")

    # ── Distribution table ────────────────────────────────────────────────────
    ax.text(0.04, 0.700, "Equipment Type Distribution",
            color=TEXT, fontsize=10, fontweight="bold")

    dist  = summary.get("type_distribution", {})
    total = sum(dist.values()) if dist else 0
    row_h = 0.052
    start_y = 0.660

    for i, (eq_type, count) in enumerate(dist.items()):
        y      = start_y - i * row_h
        pct    = count / total * 100 if total else 0
        color  = COLORS[i % len(COLORS)]
        bar_w  = 0.40 * (count / max(dist.values())) if dist else 0

        # Alternating row bg
        if i % 2 == 0:
            ax.add_patch(FancyBboxPatch((0.04, y - 0.012), 0.92, row_h - 0.004,
                boxstyle="square,pad=0", facecolor="#ffffff08", edgecolor="none"))

        # Colour dot
        ax.plot(0.065, y + 0.015, "o", color=color, markersize=5, zorder=3)

        # Type name
        ax.text(0.09, y + 0.015, eq_type, color=TEXT, fontsize=8, va="center")

        # Progress bar
        ax.add_patch(FancyBboxPatch((0.35, y + 0.005), 0.42, 0.018,
            boxstyle="round,pad=0", facecolor=BORDER, edgecolor="none"))
        if bar_w > 0:
            ax.add_patch(FancyBboxPatch((0.35, y + 0.005), bar_w, 0.018,
                boxstyle="round,pad=0", facecolor=color, edgecolor="none", alpha=0.85))

        # Count + pct
        ax.text(0.79, y + 0.015, f"{count}", color=color,
                fontsize=8, fontweight="bold", va="center", ha="right")
        ax.text(0.96, y + 0.015, f"{pct:.1f}%", color=SUBTEXT,
                fontsize=7.5, va="center", ha="right")

    # Footer line
    footer_y = max(0.08, start_y - len(dist) * row_h - 0.02)
    ax.axhline(footer_y, color=BORDER, lw=0.5, xmin=0.04, xmax=0.96)
    ax.text(0.5, footer_y - 0.03,
            "Generated by Chemical Equipment Parameter Visualizer  •  For internal use only",
            color=SUBTEXT, fontsize=7, ha="center")


# ── Page 2: Charts ────────────────────────────────────────────────────────────

def _draw_charts_page(fig, summary):
    fig.patch.set_facecolor(BG)

    # Header strip
    hax = fig.add_axes([0, 0.955, 1, 0.045])
    hax.set_facecolor(SURFACE)
    hax.axis("off")
    hax.add_patch(FancyBboxPatch((0, 0), 0.004, 1,
        boxstyle="square,pad=0", facecolor=ACCENT, edgecolor="none",
        transform=hax.transAxes))
    hax.text(0.02, 0.5, "Visual Analysis  —  Charts",
             color=TEXT, fontsize=11, fontweight="bold",
             va="center", transform=hax.transAxes)

    gs = gridspec.GridSpec(2, 2,
        left=0.06, right=0.97,
        top=0.93, bottom=0.06,
        wspace=0.30, hspace=0.42,
        figure=fig)

    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])

    _chart_distribution_bar(ax1, summary)
    _chart_donut(ax2, summary)
    _chart_gauges(ax3, summary)
    _chart_metrics_bar(ax4, summary)


def _chart_distribution_bar(ax, summary):
    dist = summary.get("type_distribution", {})
    if not dist:
        ax.text(0.5, 0.5, "No data", ha="center", color=SUBTEXT,
                transform=ax.transAxes); return

    labels = list(dist.keys())
    values = list(dist.values())
    total  = sum(values)
    y_pos  = np.arange(len(labels))

    ax.barh(y_pos, [max(values) * 1.15] * len(values),
            color=BORDER, height=0.55, zorder=1, alpha=0.3)
    for i, (y, v) in enumerate(zip(y_pos, values)):
        c = COLORS[i % len(COLORS)]
        ax.barh(y, v, color=c, height=0.55, zorder=3, alpha=0.9)
        pct = v / total * 100 if total else 0
        if v / max(values) > 0.35:
            ax.text(v - max(values)*0.02, y, f"{v} ({pct:.0f}%)",
                    va="center", ha="right", color=BG, fontsize=6.5, fontweight="bold")
        else:
            ax.text(v + max(values)*0.02, y, f"{v} ({pct:.0f}%)",
                    va="center", ha="left", color=TEXT, fontsize=6.5)

    ax.set_yticks(y_pos)
    ax.set_yticklabels(labels, color=TEXT, fontsize=7)
    ax.set_xlim(0, max(values) * 1.30)
    ax.xaxis.set_visible(False)
    ax.invert_yaxis()
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_facecolor(SURFACE)
    ax.set_title("Equipment Distribution", color=TEXT,
                 fontsize=8, fontweight="bold", pad=6, loc="left")


def _chart_donut(ax, summary):
    dist = summary.get("type_distribution", {})
    if not dist:
        ax.text(0.5, 0.5, "No data", ha="center", color=SUBTEXT,
                transform=ax.transAxes); return

    labels = list(dist.keys())
    values = list(dist.values())
    colors = [COLORS[i % len(COLORS)] for i in range(len(labels))]
    total  = sum(values)

    wedges, _ = ax.pie(values, colors=colors, startangle=90,
                       wedgeprops=dict(width=0.42, edgecolor=BG, linewidth=1.5),
                       counterclock=False)
    wedges[values.index(max(values))].set_radius(1.07)
    ax.text(0, 0, f"{total}\ntotal", ha="center", va="center",
            color=TEXT, fontsize=9, fontweight="bold", linespacing=1.4)
    ax.legend(wedges, [f"{l} {v/total*100:.0f}%" for l, v in zip(labels, values)],
              loc="lower center", bbox_to_anchor=(0.5, -0.25),
              ncol=min(3, len(labels)), fontsize=6, frameon=False,
              labelcolor=TEXT, handlelength=1)
    ax.set_facecolor(SURFACE)
    ax.set_title("Equipment Share", color=TEXT,
                 fontsize=8, fontweight="bold", pad=6, loc="left")


def _chart_gauges(ax, summary):
    metrics = [
        ("Flowrate",    "avg_flowrate",    "#4f8ef7"),
        ("Pressure",    "avg_pressure",    "#f7c948"),
        ("Temperature", "avg_temperature", "#f76c6c"),
    ]
    raw = {}
    for label, key, _ in metrics:
        v = summary.get(key)
        try:   raw[label] = float(v) if v is not None else 0.0
        except: raw[label] = 0.0

    max_val = max(raw.values()) or 1

    ax.set_xlim(0, 3); ax.set_ylim(-0.55, 1.2)
    ax.set_aspect("equal")
    ax.set_facecolor(SURFACE)
    ax.set_xticks([]); ax.set_yticks([])
    for sp in ax.spines.values(): sp.set_visible(False)
    ax.set_title("Average Metrics — Gauges", color=TEXT,
                 fontsize=8, fontweight="bold", pad=6, loc="left")

    for idx, (label, key, color) in enumerate(metrics):
        cx, cy = idx + 0.5, 0.30
        ro, ri = 0.36, 0.22
        val  = raw[label]
        pct  = val / max_val
        ang  = pct * 180

        ax.add_patch(Wedge((cx, cy), ro, 0, 180, width=ro-ri,
                           facecolor=BORDER, edgecolor="none"))
        if ang > 0:
            ax.add_patch(Wedge((cx, cy), ro, 180-ang, 180, width=ro-ri,
                               facecolor=color, edgecolor="none", alpha=0.9))
            tr = math.radians(180 - ang)
            tx = cx + (ro-(ro-ri)/2) * math.cos(tr)
            ty = cy + (ro-(ro-ri)/2) * math.sin(tr)
            ax.plot(tx, ty, "o", color=color, markersize=4,
                    markeredgecolor=BG, markeredgewidth=0.8, zorder=5)

        ax.text(cx, cy - 0.02, f"{val:.1f}", ha="center", va="center",
                color=TEXT, fontsize=8, fontweight="bold")
        ax.text(cx, cy - 0.22, label, ha="center", va="top",
                color=SUBTEXT, fontsize=6.5)
        ax.text(cx, cy - 0.34, f"{pct*100:.0f}% of max", ha="center", va="top",
                color=color, fontsize=6)


def _chart_metrics_bar(ax, summary):
    data = [
        ("Flowrate",    summary.get("avg_flowrate"),    "#4f8ef7"),
        ("Pressure",    summary.get("avg_pressure"),    "#f7c948"),
        ("Temperature", summary.get("avg_temperature"), "#f76c6c"),
    ]
    labels, values, colors = [], [], []
    for l, v, c in data:
        try:
            val = float(v) if v is not None else None
        except: val = None
        if val is not None:
            labels.append(l); values.append(val); colors.append(c)

    if not values:
        ax.text(0.5, 0.5, "No data", ha="center", color=SUBTEXT,
                transform=ax.transAxes); return

    x = np.arange(len(labels))
    max_v = max(values)

    ax.bar(x, [max_v * 1.12] * len(values), color=BORDER,
           width=0.5, zorder=1, alpha=0.3)
    bars = ax.bar(x, values, color=colors, width=0.5, zorder=3, alpha=0.9)
    for bar, val, color in zip(bars, values, colors):
        ax.text(bar.get_x() + bar.get_width()/2,
                bar.get_height() + max_v * 0.025,
                f"{val:.2f}", ha="center", va="bottom",
                color=color, fontsize=7.5, fontweight="bold")

    ax.set_xticks(x)
    ax.set_xticklabels(labels, color=TEXT, fontsize=8, fontweight="bold")
    ax.set_ylim(0, max_v * 1.22)
    ax.yaxis.set_visible(False)
    ax.set_facecolor(SURFACE)
    ax.set_title("Average Metrics", color=TEXT,
                 fontsize=8, fontweight="bold", pad=6, loc="left")
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_visible(False)
    ax.spines["bottom"].set_edgecolor(BORDER)


# ── Public entry point ────────────────────────────────────────────────────────

def export_report(summary: dict, source_label: str, parent=None):
    """
    Opens a Save dialog, then writes a 2-page dark-theme PDF:
      Page 1 — Cover: stats + distribution table
      Page 2 — Charts: 4 visual charts
    """
    default_name = "equipment_analysis_report.pdf"
    path, _ = QFileDialog.getSaveFileName(
        parent, "Save Report as PDF", default_name,
        "PDF Files (*.pdf)"
    )
    if not path:
        return   # user cancelled

    if not path.lower().endswith(".pdf"):
        path += ".pdf"

    try:
        with PdfPages(path) as pdf:
            # ── Page 1: Cover ─────────────────────────────────────────────────
            fig1 = plt.figure(figsize=(11, 8.5))
            _draw_cover(fig1, summary, source_label)
            pdf.savefig(fig1, facecolor=BG, bbox_inches="tight")
            plt.close(fig1)

            # ── Page 2: Charts ────────────────────────────────────────────────
            fig2 = plt.figure(figsize=(11, 8.5))
            _draw_charts_page(fig2, summary)
            pdf.savefig(fig2, facecolor=BG, bbox_inches="tight")
            plt.close(fig2)

            # PDF metadata
            d = pdf.infodict()
            d["Title"]   = "Chemical Equipment Analysis Report"
            d["Author"]  = "Chemical Equipment Parameter Visualizer"
            d["Subject"] = "Equipment Parameter Analysis"
            d["CreationDate"] = datetime.datetime.now()

        # Success dialog
        msg = QMessageBox(parent)
        msg.setWindowTitle("Export Successful")
        msg.setText(f"Report saved to:\n{path}")
        msg.setIcon(QMessageBox.Information)
        msg.setStyleSheet("""
            QMessageBox { background-color: #1a1f2e; }
            QMessageBox QLabel { color: #e8eaf0; font-size: 12px; min-width: 320px; }
            QPushButton {
                background: #00d4aa; color: #0e1117; border: none;
                border-radius: 7px; padding: 6px 20px; font-weight: bold;
            }
            QPushButton:hover { background: #00e8bb; }
        """)
        msg.exec_()

    except Exception as e:
        err = QMessageBox(parent)
        err.setWindowTitle("Export Failed")
        err.setText(f"Could not save PDF:\n{str(e)}")
        err.setIcon(QMessageBox.Critical)
        err.setStyleSheet("""
            QMessageBox { background-color: #1a1f2e; }
            QMessageBox QLabel { color: #f76c6c; font-size: 12px; min-width: 280px; }
            QPushButton {
                background: #f76c6c22; color: #f76c6c;
                border: 1px solid #f76c6c; border-radius: 7px; padding: 6px 20px;
            }
        """)
        err.exec_()