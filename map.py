import os
import io
from PyQt6.QtCore import QUrl
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
from PyQt6.QtWebEngineWidgets import QWebEngineView
from PyQt6.QtWebEngineCore import QWebEngineSettings
import folium
import database

class MapDisplay(QWidget):

    def __init__(self, node_ids: list, center_coord: tuple):
        super().__init__()

        self.nodes = node_ids
        self.coordinate = center_coord

        self.setWindowTitle("SafeTrack Map")
        self.setMinimumSize(800, 600)

        # Layout
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header with title and refresh button (consistent with Notifications UI)
        header_layout = QHBoxLayout()
        title_lbl = QLabel("Map")
        title_lbl.setStyleSheet("font-weight:600; font-size:16px; color:#cfd8ff;")
        header_layout.addWidget(title_lbl)
        header_layout.addStretch()
        self.refresh_btn = QPushButton("Refresh")
        # style refresh button to match notifications page controls
        self.refresh_btn.setStyleSheet("padding:6px 10px; border:1px solid #2b3a4a; border-radius:6px; background:transparent; color:#cfd8ff;")
        # clicked() passes a boolean `checked` argument; wrap to avoid
        # that boolean being interpreted as a `location` in update_map
        self.refresh_btn.clicked.connect(lambda checked=False: self.update_map())
        header_layout.addWidget(self.refresh_btn)
        layout.addLayout(header_layout)

        # Web view for map display
        self.webView = QWebEngineView()
        self.webView = QWebEngineView()

        settings = self.webView.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, True)

        # Folium map
        self.m = self.create_map(self.coordinate, 14)#folium.Map(location=self.coordinate, zoom_start=14)
        self.update_map()
        self.refresh_view()
        # give the web view a subtle border so it visually separates
        self.webView.setStyleSheet("border:1px solid #263645; border-radius:6px;")
        layout.addWidget(self.webView)

    def create_map(self, location=None, zoom_start=14):
        if location is None:
            location = self.coordinate
        tile_path = os.path.abspath("tiles").replace("\\", "/")

        m = folium.Map(
            location=location,
            zoom_start=zoom_start,
            #min_zoom=10,
            #max_zoom=16,
            tiles=None,
            attributionControl = False
        )

        folium.TileLayer(
            tiles=f"file:///{tile_path}/{{z}}/{{x}}/{{y}}.png",
            attr="Offline Map",
            control=False
        ).add_to(m)

        return m

    def update_map(self, location = None, zoom_start = 14):
        self.m = self.create_map(location, zoom_start)

        
        self.nodes = database.get_nodes()
        print(f"Updating map with nodes: {self.nodes}")

        for node in self.nodes:
            try:
                cur_gps = database.get_GPS(node)
                icon_img = os.path.abspath("images/green_icon.png")

                if database.get_status(node) == "SOS":
                    icon_img = os.path.abspath("images/red_icon.png")
                    folium.Circle(
                        radius=100,
                        location=cur_gps,
                        color='crimson',
                        fill=True
                    ).add_to(self.m)
                folium.Marker(
                    location=cur_gps,
                    popup=f"Node {node}: {cur_gps}",
                    icon=folium.CustomIcon(icon_img,icon_size=(50,50))
                ).add_to(self.m)

            except ValueError:
                print(f"***ERROR: Node {node} does not exist***")
                continue
        self.refresh_view()

    def refresh_view(self):
        data = io.BytesIO()
        self.m.save(data, close_file=False)

        html = data.getvalue().decode()

        base_url = QUrl.fromLocalFile(os.getcwd() + "/")

        self.webView.setHtml(html, base_url)

    def center_on_node(self, node_id):
        try:
            gps = database.get_GPS(node_id)
            if gps:
                self.update_map(location = gps, zoom_start = 16)
                self.refresh_view()
            else:
                print(f"***ERROR: No GPS data for node {node_id}***")
        except ValueError:
            print(f"***ERROR: Node {node_id} does not exist***")