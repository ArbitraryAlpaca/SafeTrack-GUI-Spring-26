from PyQt6.QtCore import QThread


class Monitor(QThread):
    def __init__(self, connection_port:str, rmv_after_hrs:int = 48):
        super(QThread, self).__init__()
        self.port = connection_port
        self.hrs = rmv_after_hrs
        self.time_format = "%Y-%m-%d %H:%M:%S"

    def run(self):
        import serial, database
        from datetime import datetime, timedelta
        try:
            ser = serial.Serial(self.port, 115200)
            while not self.isInterruptionRequested():
                try:
                    packets = (ser.readline().decode('utf-8').rstrip()).split(' ')
                    packet = [int(packets[0]),float(packets[1]),float(packets[2])]
                    database.add_to_db((datetime.now().strftime(self.time_format), packet[0], packet[1], packet[2], "SOS"))
                    database.delete_before_time((datetime.now() - timedelta(hours=self.hrs)).strftime(self.time_format))
                    database.delete_before_time((datetime.now() - timedelta(hours=self.hrs)).strftime(self.time_format), "notifications")
                    database.print_db()
                except ValueError:
                    pass
        except serial.SerialException:
            
            print("***ERROR: PORT NOT FOUND***")
            pass
