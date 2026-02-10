# alert_system.py
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox

class AlertSystem(QObject):
    viewNodeRequested = pyqtSignal(int)   # node_id

    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent = parent

    def show_alert(self, notification):
        msg = QMessageBox(self.parent)
        msg.setWindowTitle("Node Alert")
        msg.setIcon(QMessageBox.Icon.Warning)
        msg.setText(f"Node {notification[1]} ALERT")
        msg.setInformativeText(notification[4])

        view_btn = msg.addButton(
            "View on Map",
            QMessageBox.ButtonRole.AcceptRole
        )
        dismiss_btn = msg.addButton(
            "Dismiss",
            QMessageBox.ButtonRole.RejectRole
        )

        msg.exec()

        if msg.clickedButton() == view_btn:
            print("View on Map clicked for node", notification[1])
            self.viewNodeRequested.emit(notification[1])
