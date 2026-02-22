from PyQt6.QtCore import QThread

class Simulate(QThread):
    def __init__(self,connection_port:str,rmv_after_hrs:int = 48):
        super(QThread, self).__init__()
        self.port = connection_port
        self.hrs = rmv_after_hrs
        self.time_format = "%Y-%m-%d %H:%M:%S"

    def run(self):
        import random, time, database
        from datetime import datetime, timedelta
        while not self.isInterruptionRequested():
            node = random.randint(1,10)
            # generate latitude, longitude
            lat = round(random.uniform(33.38,33.46), 10)
            long = round(random.uniform(-111.98, -111.87), 10)

            # packet format: [node_id, latitude, longitude]
            packet = [int(node), float(lat), float(long)]  # [node_id, latitude, longitude]

            # DB expects (time, node_id, latitude, longitude, status)
            database.add_to_db((datetime.now().strftime(self.time_format), packet[0], packet[1], packet[2], "SOS"))
            database.delete_before_time((datetime.now() - timedelta(hours=self.hrs)).strftime(self.time_format))
            database.print_db()
            time.sleep(10)