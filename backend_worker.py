# backend_worker.py
from PyQt6.QtCore import QThread, pyqtSignal

class BackendWorker(QThread):
    # emits the notification tuple when one is created (optional)
    notification_signal = pyqtSignal(tuple)

    def run(self):
        import database, notification, system_notif
        database.init_db()
        database.init_notif_db()

        old_data = database.get_db()
        while not self.isInterruptionRequested():
            data = database.get_db()
            if old_data is not None and old_data != data:
                notif = notification.create_notification(data, old_data)
                if notif:
                    # create_notification already adds the notif to DB
                    # show system toast immediately
                    system_notif.new_notif(notif[3], notif[4], notif[2])
                    # emit to GUI if you want to react (but do NOT auto-refresh NotificationsPage)
                    self.notification_signal.emit(notif)
            old_data = data
            self.msleep(1000)   # sleep 1s (keeps loop responsive to requestInterruption())