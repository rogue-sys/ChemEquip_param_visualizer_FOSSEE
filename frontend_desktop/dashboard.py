# dashboard.py
from PyQt5.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QPushButton,
    QLabel,
    QFileDialog
)
from PyQt5.QtCore import QThread, pyqtSignal
import api


class UploadWorker(QThread):
    success = pyqtSignal(dict)
    error = pyqtSignal(str)

    def __init__(self, path):
        super().__init__()
        self.path = path

    def run(self):
        try:
            response = api.APIClient().upload_csv(self.path)
            if response.status_code == 201:
                self.success.emit(response.json())
            else:
                self.error.emit(response.text)
        except Exception:
            self.error.emit("Upload failed. Please try again.")


class DashboardWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Dashboard")
        self.showMaximized()

        layout = QVBoxLayout(self)
        layout.setSpacing(16)

        self.upload_btn = QPushButton("Upload CSV")
        self.history_btn = QPushButton("View History")
        self.status = QLabel("")
        self.status.setWordWrap(True)

        self.upload_btn.clicked.connect(self.pick_file)
        self.history_btn.clicked.connect(self.open_history)

        layout.addWidget(self.upload_btn)
        layout.addWidget(self.history_btn)
        layout.addWidget(self.status)

    def pick_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Select CSV file",
            "",
            "CSV Files (*.csv)"
        )

        if not path:
            return

        self.upload_btn.setDisabled(True)
        self.history_btn.setDisabled(True)
        self.status.setText("Uploading… please wait")

        self.worker = UploadWorker(path)
        self.worker.success.connect(self.upload_success)
        self.worker.error.connect(self.upload_failed)
        self.worker.start()

    def upload_success(self, dataset):
        """
        Upload → Summary navigation
        Works whether upload API returns summary or not
        """
        self.upload_btn.setEnabled(True)
        self.history_btn.setEnabled(True)
        self.status.setText("")

        # ---- Normalize dataset shape ----
        if "summary" not in dataset:
            try:
                history = api.APIClient().fetch_history().json()
                if not history:
                    self.status.setText(
                        "Upload succeeded, but no summary available."
                    )
                    return
                dataset = history[0]  # latest upload
            except Exception:
                self.status.setText("Failed to retrieve summary.")
                return
        # --------------------------------

        from summary import SummaryWindow
        self.summary_window = SummaryWindow(dataset)
        self.summary_window.show()

        # React-style navigation
        self.close()

    def upload_failed(self, message):
        self.status.setText(message)
        self.upload_btn.setEnabled(True)
        self.history_btn.setEnabled(True)

    def open_history(self):
        from history import HistoryWindow
        self.history_window = HistoryWindow()
        self.history_window.show()
