from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QSpacerItem, QSizePolicy, QMessageBox
from PyQt6.QtCore import Qt
import database

class AddNodePage(QWidget):
    """
    A page that lets the user add new nodes to a list.
    Calls a callback function when a node is added.
    """
    def __init__(self, nodes_list: list, on_node_added=None):
        """
        :param nodes_list: Reference to main node list
        :param on_node_added: Function to call when a new node is added
        """
        super().__init__()

        self.nodes = nodes_list
        self.on_node_added = on_node_added  # callback

        # Main vertical layout
        layout = QVBoxLayout()
        layout.setContentsMargins(50, 50, 50, 50)
        layout.setSpacing(20)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setLayout(layout)

        # Top spacer to center vertically
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Label
        label = QLabel("Enter new Node ID:")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setStyleSheet("font-size: 24px; font-weight: bold;")
        layout.addWidget(label)

        # Input field
        self.node_input = QLineEdit()
        self.node_input.setPlaceholderText("Node ID")
        self.node_input.setFixedWidth(300)
        self.node_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.node_input.setStyleSheet("font-size: 20px; padding: 8px;")
        layout.addWidget(self.node_input, alignment=Qt.AlignmentFlag.AlignCenter)

        # Save button
        save_btn = QPushButton("Save Node")
        save_btn.setFixedWidth(200)
        save_btn.setStyleSheet("""
            QFrame {
                background-color: #0b1220;
                color: #cfd8ff;
            }
            QPushButton {
                background: transparent;
                border: none;
                font-size: 20px;
                padding: 10px;
                text-align: center;
                color: #cfd8ff;
            }
            QPushButton:hover {
                background-color: #162040;
            }""")
        save_btn.clicked.connect(self.save_node)
        layout.addWidget(save_btn, alignment=Qt.AlignmentFlag.AlignCenter)

        # Bottom spacer to center vertically
        layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def save_node(self):
        node_id = self.node_input.text().strip()
        if node_id:
            if database.in_db(int(node_id)):
                if node_id not in self.nodes:  # avoid duplicates
                    self.nodes.append(node_id)
                    print(f"Node added: {node_id}")
                    print(f"Current nodes: {self.nodes}")

                    # Save to file
                    with open("node_ids.txt", "a") as f:
                        f.write(f"{node_id}\n")

                self.node_input.clear()
            else:
                QMessageBox.information(
                    self,
                    "WARNING",
                    f"***ERROR: NODE {node_id} DOES NOT EXIST***"
                )

                # Call callback if provided
                if self.on_node_added:
                    self.on_node_added(node_id)