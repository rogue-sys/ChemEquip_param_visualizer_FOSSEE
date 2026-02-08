# login.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton
from PyQt5.QtCore import QThread, pyqtSignal, Qt
import api


class LoginWorker(QThread):
    success = pyqtSignal(str)
    error = pyqtSignal(str)

    def __init__(self, username, password):
        super().__init__()
        self.username = username
        self.password = password

    def run(self):
        try:
            res = api.APIClient().login(self.username, self.password)
            if res.status_code == 200:
                self.success.emit(res.json()["token"])
            else:
                self.error.emit("Invalid username or password")
        except Exception:
            self.error.emit("Network error")


class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")

        self.resize(420, 320)
        self.setMinimumSize(360, 280)
        self.setWindowFlag(Qt.WindowMaximizeButtonHint, True)

        layout = QVBoxLayout(self)
        layout.setSpacing(14)

        self.username = QLineEdit()
        self.username.setPlaceholderText("Username")

        self.password = QLineEdit()
        self.password.setPlaceholderText("Password")
        self.password.setEchoMode(QLineEdit.Password)

        self.error = QLabel("")
        self.error.setObjectName("error")

        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.login)

        self.register_link = QLabel("<a href='#'>New user? Register</a>")
        self.register_link.setOpenExternalLinks(False)
        self.register_link.linkActivated.connect(self.open_register)

        for w in [self.username, self.password, self.error, self.login_btn, self.register_link]:
            layout.addWidget(w)

    def login(self):
        self.error.setText("")
        self.login_btn.setDisabled(True)

        self.worker = LoginWorker(self.username.text().strip(), self.password.text())
        self.worker.success.connect(self.success)
        self.worker.error.connect(self.fail)
        self.worker.start()

    def success(self, token):
        api.TOKEN = token
        from dashboard import DashboardWindow
        self.dashboard = DashboardWindow()
        self.dashboard.show()
        self.close()

    def fail(self, msg):
        self.error.setText(msg)
        self.login_btn.setEnabled(True)

    def open_register(self):
        from register import RegisterWindow
        self.reg = RegisterWindow()
        self.reg.show()
        self.close()
