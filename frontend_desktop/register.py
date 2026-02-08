# register.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import api


class UsernameCheckWorker(QThread):
    result = pyqtSignal(bool)

    def __init__(self, username):
        super().__init__()
        self.username = username

    def run(self):
        try:
            res = api.APIClient().check_username(self.username)
            self.result.emit(res.json().get("available", False))
        except Exception:
            self.result.emit(False)


class RegisterWorker(QThread):
    success = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        try:
            res = api.APIClient().register(self.username, self.password)
            if res.status_code in (200, 201):
                self.success.emit()
            else:
                self.error.emit("Registration failed")
        except Exception:
            self.error.emit("Network error")


class RegisterWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Register")

        self.resize(420, 340)
        self.setMinimumSize(360, 300)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")
        self.username.textChanged.connect(self.check_username)

        self.status = QLabel("")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.register_btn = QPushButton("Register")
        self.register_btn.setDisabled(True)
        self.register_btn.clicked.connect(self.register)

        for w in [self.username, self.status, self.password, self.register_btn]:
            layout.addWidget(w)

    def check_username(self):
        name = self.username.text().strip()
        if not name:
            self.status.setText("")
            self.register_btn.setDisabled(True)
            return

        self.worker = UsernameCheckWorker(name)
        self.worker.result.connect(self.on_checked)
        self.worker.start()

    def on_checked(self, available):
        if available:
            self.status.setText("✅ Username available")
            self.register_btn.setEnabled(True)
        else:
            self.status.setText("❌ Username already exists")
            self.register_btn.setDisabled(True)

    def register(self):
        self.register_btn.setDisabled(True)
        self.worker = RegisterWorker(self.username.text().strip(), self.password.text())
        self.worker.success.connect(self.done)
        self.worker.error.connect(self.error)
        self.worker.start()

    def done(self):
        from login import LoginWindow
        self.login = LoginWindow()
        self.login.show()
        self.close()

    def error(self, msg):
        self.status.setText(msg)
        self.register_btn.setEnabled(True)
