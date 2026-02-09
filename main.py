import time
import database
import notification
import system_notif
from datetime import datetime

database.init_db()
database.init_notif_db()

old_data = database.get_db()
notif = None

#testing Notifications

#test notification

'''time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
notif = (time, 0, "System","Node Reconnected", "test notification")
add_notif = database.add_notif(notif)
system_notif.new_notif(notif[3], notif[4], notif[2])'''

# python file to run code for testing purposes
# can be used to test backend code without running the entire GUI

