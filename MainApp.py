import sys
from PyQt6.QtGui import QIcon
from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedLayout
)
from PyQt6.QtCore import Qt
from map import MapDisplay
from addNode import AddNodePage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("SafeTrack")
        self.setMinimumSize(1200, 700)

        # ================= CENTRAL WIDGET =================
        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ================= SIDEBAR =================
        self.sidebar_buttons_info = [
            ("btnMap", "Map"),
            ("btnAddNode", "Add Node"),
            ("btnSOS", "SOS"),
            ("btnNotifications", "Notifications"),
            ("btnSettings", "Settings"),
        ]
        self.sidebar_buttons = {}
        sidebar = QFrame()
        sidebar.setFixedWidth(200)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0b1220;
                color: #cfd8ff;
            }
            QPushButton {
                background: transparent;
                border: none;
                padding: 8px;
                text-align: left;
                color: #cfd8ff;
            }
            QPushButton:hover {
                background-color: #162040;
            }
        """)

        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(12, 12, 12, 12)
        sidebar_layout.setSpacing(12)

        title = QLabel("SafeTrack")
        title.setStyleSheet("font-size:16px; font-weight:600;")
        sidebar_layout.addWidget(title)

        for obj_name, label in self.sidebar_buttons_info:
            icons = {"Map": r"images\map_icon.png",
                     "Add Node": r"images\add_icon.png",
                     "SOS": r"images\alert_icon.png",
                     "Notifications": r"images\notifications_icon.png",
                     "Settings": r"images\settings.png"}
            icn_sizes = {"Map": 30,
                         "Add Node": 30,
                         "SOS": 30,
                         "Notifications": 30,
                         "Settings":30}
            icon = QIcon(icons[label])
            btn = QPushButton(label)
            btn.setIcon(icon)
            btn.setIconSize(QSize(icn_sizes[label],icn_sizes[label]))
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons[obj_name] = btn
            btn.clicked.connect(lambda checked, name=obj_name: self.on_sidebar_button(name))

        sidebar_layout.addStretch()
        root_layout.addWidget(sidebar)

        # ================= MAIN AREA =================
        main_area = QWidget()
        main_area.setStyleSheet("""
            background-color: #070b14;
            color: #cfd8ff;
        """)
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(10, 10, 10, 10)
        main_layout.setSpacing(10)
        root_layout.addWidget(main_area)

        # -------- CONTENT AREA --------
        content_layout = QHBoxLayout()
        content_layout.setSpacing(10)
        main_layout.addLayout(content_layout)

        # Use stacked layout for switching pages
        self.stacked_layout = QStackedLayout()
        content_frame = QFrame()
        content_frame.setLayout(self.stacked_layout)
        content_layout.addWidget(content_frame)

        self.blank_pages = {}
        # ----- MAP PAGE -----
        self.nodes = []
        try:
            with open("node_ids.txt", "r") as f:
                self.nodes = [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            # File doesn't exist yet, start with empty list
            self.nodes = []

        print(f"Loaded nodes: {self.nodes}")
        self.center = (33.42057834806449, -111.9322007773111)
        self.map_widget = MapDisplay(
            node_ids=self.nodes,
            center_coord=self.center
        )

        self.map_widget = MapDisplay(self.nodes, center_coord=self.center)
        self.stacked_layout.addWidget(self.map_widget)

        # Add Node page with callback
        add_node_page = AddNodePage(
            nodes_list=self.nodes,
            on_node_added=self.node_added_callback
        )
        self.stacked_layout.addWidget(add_node_page)

        # ----- BLANK PAGES FOR OTHER BUTTONS -----
        for idx, (obj_name, label) in enumerate(self.sidebar_buttons_info[1:], start=1):
            page = QFrame()
            layout = QVBoxLayout(page)
            label_widget = QLabel(f"{label} screen (blank)")
            label_widget.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(label_widget)
            self.stacked_layout.addWidget(page)
            self.blank_pages[obj_name] = page

        # Default page = MAP
        self.stacked_layout.setCurrentIndex(0)

    def on_sidebar_button(self, name):

        if name == "btnMap":
            self.stacked_layout.setCurrentIndex(0)
        elif name == "btnAddNode":
            self.stacked_layout.setCurrentIndex(1)
        else:
            idx = list(self.blank_pages.keys()).index(name) + 2
            self.stacked_layout.setCurrentIndex(idx)
        print(f"Button pressed: {name}")

    def node_added_callback(self, node_id):

        print(f"Callback: New node {node_id} added, refreshing map...")
        self.map_widget.update_map()
        self.map_widget.refresh_view()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
