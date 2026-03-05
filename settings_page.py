from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QFrame

import theme


class SettingsPage(QWidget):
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self._theme_name = theme.load_theme_name()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Settings")
        title.setStyleSheet("font-size:18px; font-weight:700;")
        layout.addWidget(title)

        card = QFrame()
        card_layout = QVBoxLayout(card)
        card_layout.setContentsMargins(16, 16, 16, 16)
        card_layout.setSpacing(12)

        row = QHBoxLayout()
        row.addWidget(QLabel("Theme"))
        row.addStretch()

        self.theme_btn = QPushButton()
        self.theme_btn.setCheckable(True)
        self.theme_btn.clicked.connect(self.on_theme_clicked)
        self.theme_btn.setMinimumWidth(90)

        self.theme_btn.setStyleSheet("""
        QPushButton {
            border-radius: 12px;
            padding: 6px 14px;
            border: 1px solid rgba(120,120,120,0.4);
        }

        QPushButton:hover {
            background-color: rgba(120,120,120,0.15);
        }

        QPushButton:checked {
            background-color: rgba(120,120,120,0.25);
        }
        """)
        row.addWidget(self.theme_btn)

        card_layout.addLayout(row)
        layout.addWidget(card)
        layout.addStretch()

        self.sync_ui()

    def sync_ui(self):
        is_dark = (self._theme_name == "dark")

        self.theme_btn.blockSignals(True)
        self.theme_btn.setChecked(is_dark)
        self.theme_btn.setText("Dark" if is_dark else "Light")
        self.theme_btn.blockSignals(False)

    def apply_theme(self, theme_name: str):
        self._theme_name = theme_name
        self.sync_ui()

    def on_theme_clicked(self):
        new_theme = "light" if self._theme_name == "dark" else "dark"
        self.main_window.apply_theme(new_theme)