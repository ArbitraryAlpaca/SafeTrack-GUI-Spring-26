# main.py — simple SOS map with on-screen alert dialogs + map update
import sys
import io
from datetime import datetime

import folium
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView

import database

# CONFIG
REFRESH_SECONDS = 10        # how often we check DB and refresh map
MAP_ZOOM = 13
MAP_CENTER = (33.415216, -111.928240)
DB_PATH = "nodes.db"

# track nodes we've already alerted so we only pop once until cleared
already_alerted = set()


def get_all_node_ids(db: str = DB_PATH):
    try:
        with __import__("sqlite3").connect(db) as conn:
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT node_id FROM nodes")
            rows = cur.fetchall()
            return [int(r[0]) for r in rows]
    except Exception:
        return []


class MapWindow(QWidget):
    def __init__(self, center=MAP_CENTER, zoom_start=MAP_ZOOM):
        super().__init__()
        self.setWindowTitle("SafeTrack - SOS Map")
        self.resize(1000, 700)

        self.center = center
        self.zoom_start = zoom_start

        layout = QVBoxLayout()
        self.setLayout(layout)

        self.web = QWebEngineView()
        layout.addWidget(self.web)

        # timer to refresh map periodically
        self.timer = QTimer(self)
        self.timer.setInterval(REFRESH_SECONDS * 1000)
        self.timer.timeout.connect(self.refresh_map)
        self.timer.start()

        self.refresh_map()

    def refresh_map(self):
        """
        Rebuilds the folium map from DB. Marks ALERT nodes red and shows a dialog
        the first time we detect a node newly in ALERT.
        """
        try:
            m = folium.Map(location=self.center, zoom_start=self.zoom_start)

            node_ids = get_all_node_ids()
            for nid in node_ids:
                # get most recent GPS & status (from your database.py helpers)
                gps = database.get_GPS(nid)
                status = (database.get_status(nid) or "").strip().upper()

                if not gps or len(gps) != 2:
                    continue

                lat, lon = gps[0], gps[1]

                time_sent = ""
                # try to retrieve time from get_recent_info if exists
                try:
                    rec = database.get_recent_info(nid)
                    if rec and len(rec) > 0:
                        # rec is a list with a tuple like (time,node_id,lon,lat,status)
                        time_sent = rec[0][0]
                except Exception:
                    pass

                popup_text = f"Node {nid}<br>Location: {lat:.6f}, {lon:.6f}<br>Time: {time_sent or 'N/A'}"

                if status == "ALERT":
                    # red marker + highlight circle
                    folium.Circle(location=(lat, lon), radius=100, color="crimson", fill=True, fill_opacity=0.35).add_to(m)
                    folium.Marker(location=(lat, lon),
                                  popup=folium.Popup(popup_text, max_width=300),
                                  icon=folium.Icon(color="red", icon="exclamation-triangle")).add_to(m)

                    # show a one-time modal dialog for this node (only when newly alerted)
                    if nid not in already_alerted:
                        already_alerted.add(nid)
                        # Use Qt's event loop to show a non-blocking modal
                        self.show_alert_dialog(nid, lat, lon, time_sent)

                else:
                    # normal green marker
                    folium.Marker(location=(lat, lon),
                                  popup=folium.Popup(popup_text, max_width=300),
                                  icon=folium.Icon(color="green", icon="info-sign")).add_to(m)
                    # if previously alerted but now cleared, allow future alerts
                    if nid in already_alerted:
                        already_alerted.remove(nid)

            # render map HTML and push to web view
            data = io.BytesIO()
            m.save(data, close_file=False)
            html = data.getvalue().decode()
            self.web.setHtml(html)
            print(f"[{datetime.now().strftime('%H:%M:%S')}] Map refreshed — nodes: {len(node_ids)}")
        except Exception as e:
            print("Error refreshing map:", e)

    def show_alert_dialog(self, node_id, lat, lon, time_sent):
        """
        Show a modal info dialog on-screen for an alert. Non-blocking: it uses
        Qt to display a dialog but won't stop the map refresh timer.
        """
        title = f"ALERT — Node {node_id}"
        body = f"Node ID: {node_id}\nLocation: {lat:.6f}, {lon:.6f}\nTime Sent: {time_sent or 'N/A'}"
        # create a QMessageBox; it will appear on top of the map window
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(body)
        msg.setIcon(QMessageBox.Warning)
        msg.setStandardButtons(QMessageBox.Ok)
        # show without blocking other events (exec_ would block)
        msg.show()
        # optional: auto-close after X ms (uncomment to enable)
        # QTimer.singleShot(5000, msg.accept)  # close after 5s


def main():
    # make sure DB/table exists (uses your database.init_db)
    database.init_db(DB_PATH)

    app = QApplication(sys.argv)
    win = MapWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()