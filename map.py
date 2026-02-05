import sys
import io
import folium
import database
from PyQt5.QtWidgets import QApplication, QWidget, QHBoxLayout, QVBoxLayout
from PyQt5.QtWebEngineWidgets import QWebEngineView


class MapDisplay(QWidget):
    def __init__(self,node_ids:list,center_coord:tuple):
        super().__init__()
        self.nodes = node_ids
        self.setWindowTitle("Map")
        self.window_width, self.window_height = 1600, 1200
        self.setMinimumSize(self.window_width, self.window_height)
        layout = QVBoxLayout()
        self.setLayout(layout)


        self.coordinate = center_coord
        m = folium.Map(
            title = 'SafeTrack',
            zoom_start=14,
            location=self.coordinate
        )
        self.update_map(self.nodes, m)

        data = io.BytesIO()
        m.save(data, close_file=False)

        webView = QWebEngineView()
        webView.setHtml(data.getvalue().decode())
        layout.addWidget(webView)

    def update_map(self,node_ids:list,m) -> None:
        for node in node_ids:
            popup_color = 'green'
            cur_gps = database.get_GPS(node)
            try:
                if database.get_status(node) == "ALERT":
                    popup_color = 'red'
                    folium.Circle(
                        radius = 100,
                        location = cur_gps,
                        color = 'crimson',
                        fill = True
                    ).add_to(m)

                folium.Marker(
                    database.get_GPS(node),
                    popup = f"Node {node}: {cur_gps}",
                    icon = folium.Icon(color = popup_color,icon = 'info-sign')
                ).add_to(m)
            except ValueError:
                print(f"***ERROR: Node {node} Does Not Exist***")
                continue


app = QApplication(sys.argv)

"""app.setStyleSheet('''
    QWidget{
        font-size: 35px;
    }
''')"""
myApp = MapDisplay(["1","2","3","5"],(33.415216, -111.928240))
myApp.show()
sys.exit(app.exec_())
