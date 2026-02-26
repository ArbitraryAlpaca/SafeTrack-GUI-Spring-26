# ----------------- Notifications Backend -----------------

# Notif = (time, node_id, status, title, message)

import database
from datetime import datetime

def _parse_time(val: str) -> datetime:
    try:
        return datetime.fromisoformat(val)
    except Exception:
        try:
            return datetime.strptime(val, "%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.min


def create_notification(data: list[tuple], old_data: list[tuple]) -> list[tuple]:
    """Compare `data` and `old_data` per-node and return only new
    notifications for added/removed nodes and meaningful updates.
    - status changes (inactive/active/SOS) produce status notifications
    - location changes (lat/lon) produce location notifications
    - time-only changes produce no notification
    """
    new_notifs: list[tuple] = []

    # build latest-row lookup by node_id for both datasets
    def to_dict(rows: list[tuple]) -> dict:
        # expected row format: (time, node_id, latitude, longitude, status)
        d = {}
        for r in rows:
            node = r[1]  
            d[node] = r
        return d

    new_dict = to_dict(data)
    old_dict = to_dict(old_data)

    new_nodes = set(new_dict.keys())
    old_nodes = set(old_dict.keys())

    # Added nodes
    for node in new_nodes - old_nodes:
        n = new_row_notifications(new_dict[node])
        new_notifs.append(n)

    # Removed nodes
    for node in old_nodes - new_nodes:
        n = removed_row_notifications(old_dict[node])
        new_notifs.append(n)

    # Updated nodes (present in both) -> decide if status/location changed
    for node in new_nodes & old_nodes:
        old_row = old_dict[node]
        new_row = new_dict[node]
        n = updated_row_notifications(old_row, new_row)
        if n:
            new_notifs.append(n)

    return new_notifs

def new_row_notifications(data: tuple) -> tuple:
    # Title should describe the event; status/type goes in the third field.
    if data[4] == "SOS":
        title = f"New Node {data[1]} SOS Alert"
        # data[2] = latitude, data[3] = longitude
        message = f"Current location: {data[2]:.6f}, {data[3]:.6f}"
        n = (data[0], data[1], "SOS", title, message)
    else:
        title = f"Node {data[1]} has been added"
        message = f"Current location: {data[2]:.6f}, {data[3]:.6f}"
        n = (data[0], data[1], "System", title, message)
    database.add_notif(n)
    return n

def removed_row_notifications(data: tuple) -> tuple:
    title = f"Node {data[1]} has been removed"
    message = f"Last recorded location: {data[2]:.6f}, {data[3]:.6f}"
    n = (data[0], data[1], "System", title, message)
    database.add_notif(n)
    return n

def updated_row_notifications(old_row: tuple, new_row: tuple) -> tuple:
    """Compare an old_row and new_row for a node and return a notification
    tuple if a meaningful change occurred; otherwise return None.
    """
    # expected row format: (time, node_id, latitude, longitude, status)
    try:
        old_status = str(old_row[4])
        new_status = str(new_row[4])
        # stored as (latitude, longitude)
        old_lat, old_lon = float(old_row[2]), float(old_row[3])
        new_lat, new_lon = float(new_row[2]), float(new_row[3])
    except Exception:
        return None

    node = new_row[1]
    # Status change has priority
    if old_status != new_status:
        if new_status == "SOS":
            title = f"Node {node} SOS Alert"
            # new_lat, new_lon computed from new_row (lat, long)
            message = f"Location: {new_lat:.6f}, {new_lon:.6f}"
            n = (new_row[0], node, "SOS", title, message)
        elif new_status == "inactive":
            title = f"Node {node} Disconnected"
            message = f"Last known location: {new_lat:.6f}, {new_lon:.6f}"
            n = (new_row[0], node, "Alert", title, message)
        elif new_status == "active":
            title = f"Node {node} Reconnected"
            message = f"Present location: {new_lat:.6f}, {new_lon:.6f}"
            n = (new_row[0], node, "Alert", title, message)
        else:
            title = f"Node {node} Status: {new_status}"
            message = f"Location: {new_lat:.6f}, {new_lon:.6f}"
            n = (new_row[0], node, "Info", title, message)
        database.add_notif(n)
        return n

    # No status change -> check location change (consider small epsilon)
    eps = 1e-6
    if abs(old_lat - new_lat) > eps or abs(old_lon - new_lon) > eps:
        title = f"Node {node} Location Update"
        message = f"Location: {new_lat:.6f}, {new_lon:.6f}"
        n = (new_row[0], node, "Info", title, message)
        database.add_notif(n)
        return n

    # Only time changed or identical -> no notification
    return None


# ----------------- PyQt6 Notifications Page (UI) -----------------

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QScrollArea,
    QFrame, QLabel, QComboBox, QSizePolicy
)
from PyQt6.QtCore import Qt


class NotificationsPage(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.notifs = []  # cached notifications (only updated on refresh)

        self.setMinimumSize(600, 400)

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Header / controls
        header_layout = QHBoxLayout()
        self.refresh_btn = QPushButton("Refresh")
        # slightly stronger visual for controls
        self.refresh_btn.setStyleSheet("padding:6px 10px; border:1px solid #2b3a4a; border-radius:6px;")
        self.filter_combo = QComboBox()
        self.filter_combo.setStyleSheet("padding:4px; border:1px solid #2b3a4a; border-radius:6px;")
        # filter options: All, SOS, Alert, Info, System
        self.filter_combo.addItems(["All", "SOS", "Alert", "Info", "System"])
        header_layout.addWidget(QLabel("Notifications"))
        header_layout.addStretch()
        header_layout.addWidget(self.filter_combo)
        header_layout.addWidget(self.refresh_btn)
        layout.addLayout(header_layout)

        # Scrollable list container for notification 'cards'
        self.scroll = QScrollArea()
        self.scroll.setWidgetResizable(True)
        self.scroll_content = QFrame()
        self.scroll_layout = QVBoxLayout()
        self.scroll_layout.setContentsMargins(8, 8, 8, 8)
        self.scroll_layout.setSpacing(8)
        self.scroll_content.setLayout(self.scroll_layout)
        self.scroll.setWidget(self.scroll_content)
        layout.addWidget(self.scroll)

        # Connections
        self.refresh_btn.clicked.connect(self.load_notifications)
        self.filter_combo.currentIndexChanged.connect(self.on_filter_changed)

        # Filter state: None or lowercase string
        self.current_filter = None

    def load_notifications(self):
        """Fetch notifications from the DB and populate the list of cards.
        Intentionally only called when the Refresh button is pressed."""
        self.notifs = database.get_notifs()
        self.current_filter = None
        self._populate_list(self.notifs)

    def _clear_list(self):
        while self.scroll_layout.count():
            child = self.scroll_layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def _populate_list(self, rows):
        self._clear_list()
        for r in rows:
            # expected row format: (time, node_id, status, Title, Message)
            time = str(r[0]) if len(r) > 0 else ""
            node_id = str(r[1]) if len(r) > 1 else ""
            status = str(r[2]) if len(r) > 2 else ""
            title = str(r[3]) if len(r) > 3 else ""
            message = str(r[4]) if len(r) > 4 else ""

            card = QFrame()
            card.setFrameShape(QFrame.Shape.StyledPanel)
            # keep a subtle background and rounded corners but remove inner borders
            card.setStyleSheet("background-color: #0f1724; border-radius:8px;")
            card.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            card_layout = QHBoxLayout()
            card_layout.setContentsMargins(8, 8, 8, 8)

            # Left: title and message (vertical)
            left = QVBoxLayout()
            title_lbl = QLabel(title)
            title_lbl.setStyleSheet("font-weight: 600; font-size: 14px;")
            msg_lbl = QLabel(message)
            msg_lbl.setWordWrap(True)
            left.addWidget(title_lbl)
            left.addWidget(msg_lbl)

            # Right: status and time
            right = QVBoxLayout()
            status_lbl = QLabel(status)
            status_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            status_lbl.setStyleSheet("font-weight: 700; color: #c0392b;")
            time_lbl = QLabel(time)
            time_lbl.setAlignment(Qt.AlignmentFlag.AlignRight)
            time_lbl.setStyleSheet("font-size: 10px; color: gray;")
            right.addWidget(status_lbl)
            right.addWidget(time_lbl)

            card_layout.addLayout(left)
            card_layout.addLayout(right)
            card.setLayout(card_layout)

            self.scroll_layout.addWidget(card)

        # add stretch at bottom
        self.scroll_layout.addStretch()

    def on_filter_changed(self, index: int):
        """Apply the dropdown filter to the cached notifications.
        Does not query the DB; only filters in-memory list.
        Options: All, Alert, System"""
        choice = self.filter_combo.currentText()
        if choice == "All":
            self.current_filter = None
            self._populate_list(self.notifs)
            return

        # match status column (index 2) case-insensitively
        wanted = choice.lower()
        filtered = [r for r in self.notifs if len(r) > 2 and str(r[2]).lower() == wanted]
        self.current_filter = wanted
        self._populate_list(filtered)


