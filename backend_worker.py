# backend_worker.py
from PyQt6.QtCore import QThread, pyqtSignal

class BackendWorker(QThread):
    # emits the notification tuple when one is created (optional)
    notification_signal = pyqtSignal(tuple)

    def run(self):
        import database, notification, system_notif

        old_data = database.get_db()
        x = 0
        if x == 0:
            print("Initial data:", old_data)
            x += 1
        while not self.isInterruptionRequested():
            data = database.get_db()
            if old_data is not None and old_data != data:
                notif = notification.create_notification(data, old_data)
                if notif:
                    # create_notification already adds the notif to DB
                    # show system toast immediately
                    for n in notif:
                        system_notif.new_notif(n[3], n[4], n[2])
                        print("Backend notif:", n)
                        # emit to GUI if you want to react (but do NOT auto-refresh NotificationsPage)
                        self.notification_signal.emit(n)
            old_data = data
            self.msleep(1000)   # sleep 1s (keeps loop responsive to requestInterruption())