# backend_worker.py
from PyQt6.QtCore import QThread, pyqtSignal
from user import User

class BackendWorker(QThread):
    # emits the notification tuple when one is created (optional)
    notification_signal = pyqtSignal(tuple)
    def __init__(self, user:User):
        super(QThread, self).__init__()
        self.user = user

    def run(self):
        import database, notification, system_notif

        old_data = database.get_db()
        
        while not self.isInterruptionRequested():
            data = database.get_db()
            if old_data is not None and old_data != data:
                notif = notification.create_notification(data, old_data)
                if notif:
                    # create_notification already adds the notif to DB
                    # show system toast immediately
                    for n in notif:
                        # redact location only for nodes the user is NOT authorized to view
                        if not self.user.is_admin or n[1] not in self.user.viewable_nodes:
                            n = self.redacted_notif(n)
                        system_notif.new_notif(n[3], n[4], n[2])
                        print("Backend notif:", n)
                        # emit to GUI if you want to react (but do NOT auto-refresh NotificationsPage)
                        self.notification_signal.emit(n)
            old_data = data
            self.msleep(1000)   # sleep 1s (keeps loop responsive to requestInterruption())
    
    def redacted_notif(self, notif:tuple) -> tuple:
        # Redact location info for unauthorized nodes; keep other details for alerting.
        import re
        pattern = r"(?<=Location: ).*"
        redacted_message = re.sub(pattern, "(UNAUTHORIZED)", notif[4])
        return (notif[0], notif[1], notif[2], notif[3], redacted_message)