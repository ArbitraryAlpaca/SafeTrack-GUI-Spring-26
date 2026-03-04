# settings_window.py
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QSpinBox,
    QCheckBox, QPushButton, QTabWidget, QWidget, QLabel, QComboBox
)
from PyQt6.QtCore import pyqtSignal
from settings import settings


class SettingsWindow(QDialog):
    settings_changed = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self._build_ui()
        self._load_values()

    def _build_ui(self):
        layout = QVBoxLayout(self)

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        # --- Serial tab ---
        self.serial_tab = QWidget()
        serial_layout = QFormLayout(self.serial_tab)
        self.port_input = QLineEdit()
        self.baud_input = QSpinBox()
        self.baud_input.setRange(300, 115200)
        self.auto_connect_checkbox = QCheckBox("Auto-connect on startup")
        serial_layout.addRow("Serial port", self.port_input)
        serial_layout.addRow("Baudrate", self.baud_input)
        serial_layout.addRow("", self.auto_connect_checkbox)
        self.tabs.addTab(self.serial_tab, "Serial")

        # --- Notifications tab ---
        self.notif_tab = QWidget()
        notif_layout = QFormLayout(self.notif_tab)
        self.notif_enable_checkbox = QCheckBox("Enable notifications")
        self.notif_sound_checkbox = QCheckBox("Play sound for alerts")
        notif_layout.addRow(self.notif_enable_checkbox)
        notif_layout.addRow(self.notif_sound_checkbox)
        self.tabs.addTab(self.notif_tab, "Notifications")

        # --- UI tab (controls for GUI elements) ---
        self.ui_tab = QWidget()
        ui_layout = QFormLayout(self.ui_tab)

        # Sidebar color (simple text field expecting hex like #0b1220)
        self.sidebar_color_input = QLineEdit()
        ui_layout.addRow("Sidebar color (hex)", self.sidebar_color_input)

        # Sidebar width
        self.sidebar_width_input = QSpinBox()
        self.sidebar_width_input.setRange(100, 600)
        ui_layout.addRow("Sidebar width (px)", self.sidebar_width_input)

        # Sidebar position
        self.sidebar_pos_input = QComboBox()
        self.sidebar_pos_input.addItems(["left", "right"])
        ui_layout.addRow("Sidebar position", self.sidebar_pos_input)

        # Map scale as percent of main area width
        self.map_scale_input = QSpinBox()
        self.map_scale_input.setRange(30, 100)
        ui_layout.addRow("Map width % of window", self.map_scale_input)

        # Theme (light / dark)
        self.theme_input = QComboBox()
        self.theme_input.addItems(["dark", "light"])
        ui_layout.addRow("Theme", self.theme_input)

        self.tabs.addTab(self.ui_tab, "UI / Layout")

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_layout.addWidget(self.save_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        # Connections
        self.save_btn.clicked.connect(self._on_save)
        self.cancel_btn.clicked.connect(self.reject)

    def _load_values(self):
        # Serial
        self.port_input.setText(str(settings.get("serial", "port", default="COM9") or ""))
        self.baud_input.setValue(int(settings.get("serial", "baudrate", default=9600) or 9600))
        self.auto_connect_checkbox.setChecked(bool(settings.get("serial", "auto_connect", default=False)))

        # Notifications
        self.notif_enable_checkbox.setChecked(bool(settings.get("notifications", "enabled", default=True)))
        self.notif_sound_checkbox.setChecked(bool(settings.get("notifications", "sound", default=True)))

        # UI
        self.sidebar_color_input.setText(str(settings.get("ui", "sidebar_color", default="#0b1220") or "#0b1220"))
        self.sidebar_width_input.setValue(int(settings.get("ui", "sidebar_width", default=200) or 200))
        pos = settings.get("ui", "sidebar_position", default="left") or "left"
        idx = self.sidebar_pos_input.findText(pos)
        if idx >= 0:
            self.sidebar_pos_input.setCurrentIndex(idx)
        self.map_scale_input.setValue(int(settings.get("ui", "map_scale_percent", default=70) or 70))
        theme = settings.get("ui", "theme", default="dark") or "dark"
        tidx = self.theme_input.findText(theme)
        if tidx >= 0:
            self.theme_input.setCurrentIndex(tidx)

    def _on_save(self):
        # write back to settings model
        settings.set(self.port_input.text(), "serial", "port")
        settings.set(int(self.baud_input.value()), "serial", "baudrate")
        settings.set(bool(self.auto_connect_checkbox.isChecked()), "serial", "auto_connect")

        settings.set(bool(self.notif_enable_checkbox.isChecked()), "notifications", "enabled")
        settings.set(bool(self.notif_sound_checkbox.isChecked()), "notifications", "sound")

        settings.set(self.sidebar_color_input.text(), "ui", "sidebar_color")
        settings.set(int(self.sidebar_width_input.value()), "ui", "sidebar_width")
        settings.set(self.sidebar_pos_input.currentText(), "ui", "sidebar_position")
        settings.set(int(self.map_scale_input.value()), "ui", "map_scale_percent")
        settings.set(self.theme_input.currentText(), "ui", "theme")

        # emit signal so whoever opened the dialog can react
        self.settings_changed.emit()
        self.accept()