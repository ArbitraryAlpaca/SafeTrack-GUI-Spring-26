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

# data = [(time, node_id, longitude, latitude, status), ...]
#notif = (time, node_id, status, title, message)


data = [(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 5, 33.331946454694378, -111.83544878156348, "active")]
for row in data:
    database.add_to_db(row)


# python file to run code for testing purposes
# can be used to test backend code without running the entire GUI

