# charts.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure


class ChartsWindow(QWidget):
    def __init__(self, summary):
        super().__init__()
        self.setWindowTitle("Charts")

        self.resize(800, 500)
        self.setMinimumSize(600, 400)

        layout = QVBoxLayout(self)

        fig = Figure()
        canvas = FigureCanvasQTAgg(fig)
        ax = fig.add_subplot(111)

        numeric = {k: v for k, v in summary.items() if isinstance(v, (int, float))}

        if not numeric:
            ax.text(0.5, 0.5, "No numeric data available", ha="center")
        else:
            ax.bar(numeric.keys(), numeric.values())

        layout.addWidget(canvas)
