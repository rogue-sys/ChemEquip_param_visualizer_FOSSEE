# history.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QListWidget, QLabel
from PyQt5.QtCore import QThread, pyqtSignal
from datetime import datetime
import api


class HistoryWorker(QThread):
    success = pyqtSignal(list)

    def run(self):
        res = api.APIClient().fetch_history()
        self.success.emit(res.json())


class HistoryWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("History")
        self.showMaximized()

        layout = QVBoxLayout(self)
        self.list = QListWidget()
        self.info = QLabel("")

        layout.addWidget(self.list)
        layout.addWidget(self.info)

        self.worker = HistoryWorker()
        self.worker.success.connect(self.populate)
        self.worker.start()

        self.list.itemClicked.connect(self.open_summary)

    def populate(self, data):
        if not data:
            self.info.setText("No history yet…")
            return

        self.data = data
        for item in data:
            dt = datetime.fromisoformat(item["uploaded_at"])
            self.list.addItem(
                f'{item["filename"]} | {dt.strftime("%d %b %Y, %H:%M")}'
            )

    def open_summary(self):
        from summary import SummaryWindow
        idx = self.list.currentRow()
        self.summary = SummaryWindow(self.data[idx])
        self.summary.show()
