# summary.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QTextEdit,
    QPushButton,
    QMessageBox
)
import json


class SummaryWindow(QWidget):
    def __init__(self, dataset):
        super().__init__()
        self.setWindowTitle("Summary")
        self.showMaximized()

        # ---- Defensive check (CRITICAL) ----
        if "summary" not in dataset:
            QMessageBox.critical(
                self,
                "Summary Error",
                "Summary data not available for this dataset."
            )
            self.close()
            return
        # -----------------------------------

        layout = QVBoxLayout(self)

        self.text = QTextEdit()
        self.text.setReadOnly(True)
        self.text.setText(json.dumps(dataset["summary"], indent=4))

        self.view_charts_btn = QPushButton("View Charts")
        self.view_charts_btn.clicked.connect(self.open_charts)

        layout.addWidget(self.text)
        layout.addWidget(self.view_charts_btn)

        self.summary = dataset["summary"]

    def open_charts(self):
        from charts import ChartsWindow
        self.charts_window = ChartsWindow(self.summary)
        self.charts_window.show()
