# ----------------- Notifications Backend -----------------

# Notif = (time, node_id, status, title, message)

import database

notif = []

def create_notification(data: list[tuple], old_data: list[tuple]) -> list[tuple] | None:
    global notif
    length = len(data)
    if len(data) > len(old_data):
        length = len(old_data)
        added_data = list(set(data) - set(old_data))
        notif.append(new_row_notifications(added_data))
        print("Added data:", added_data)
        n = updated_row_notifications(added_data[0])
        if n:
            notif.append(n)


    elif len(data) < len(old_data):
        removed_data = list(set(old_data) - set(data))
        notif.append(removed_row_notifications(removed_data))
    
    for i in range(length):
        if data[i][0] != old_data[i][0]:
            notif.append(updated_row_notifications(data[i]))

    return notif

def new_row_notifications(data: list[tuple]) -> tuple:
    n = (data[0][0],data[0][1],"System","Info",f"Node {data[0][1]} has been added")
    database.add_notif(n)
    return n

def removed_row_notifications(data: list[tuple]) -> tuple:
    n = (data[0][0],data[0][1],"System","Info",f"Node {data[0][1]} has been removed")
    database.add_notif(n)
    return n

def updated_row_notifications(data: tuple) -> tuple:
    n = None
    comparator = data[-1]
    print("Comparator:", comparator)
    if comparator == "SOS":
        n = (data[0],data[1],"SOS","Warning",f"Node {data[1]} SOS Alert.\n\nLocation: ({data[2]}, {data[3]})")
        print("SOS Alert for node", data[1])
        database.add_notif(n)
    elif comparator == "inactive":
        n = (data[0],data[1],"Alert","Warning",f"Node {data[1]} disconnected. \n\nLast known location: ({data[2]}, {data[3]})")
        database.add_notif(n)
    elif comparator == "active":
        n = (data[0],data[1],"Alert","Info",f"Node {data[1]} reconnected. \n\nPresent location: ({data[2]}, {data[3]})")
        database.add_notif(n)

    print("Updated data:", data)

    return n


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
        self.filter_combo = QComboBox()
        # filter options: All, Alert, System
        self.filter_combo.addItems(["All", "Alert", "System"])
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


