import sys
import os

from PyQt6.QtGui import QIcon, QFont, QPainter, QColor, QPen
from PyQt6.QtCore import QSize, Qt, pyqtSignal, QRect
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout,
    QPushButton, QLabel, QFrame, QStackedLayout,
    QMessageBox
)

import database
import auth_database as adb
from login import User, LoginWindow

from map import MapDisplay
from notification import NotificationsPage
from backend_worker import BackendWorker
from alert_system import AlertSystem
from simulating_nodes import Simulate  # for debugging only
from settings import SettingsPage


# ═══════════════════════════════════════════════════════
# CUSTOM WIDGETS
# ═══════════════════════════════════════════════════════

class AvatarWidget(QWidget):
    """Circular avatar showing user initials."""
    def __init__(self, initials: str, size: int = 36, parent=None):
        super().__init__(parent)
        self.initials = initials.upper()[:2]
        self.setFixedSize(size, size)
        self._size = size

    def paintEvent(self, event):
        p = QPainter(self)
        p.setRenderHint(QPainter.RenderHint.Antialiasing)
        p.setBrush(QColor("#2563eb"))
        p.setPen(QPen(QColor("#3b82f6"), 1.5))
        p.drawEllipse(2, 2, self._size - 4, self._size - 4)
        p.setPen(QColor("#ffffff"))
        font = QFont("SF Pro Display", int(self._size * 0.32))
        font.setWeight(QFont.Weight.DemiBold)
        p.setFont(font)
        p.drawText(QRect(0, 0, self._size, self._size),
                   Qt.AlignmentFlag.AlignCenter, self.initials)
        p.end()


class SidebarButton(QPushButton):
    """Nav button with left accent bar when active."""
    def __init__(self, text: str, icon_path: str = "", parent=None):
        super().__init__(text, parent)
        self._active = False
        if icon_path and os.path.exists(icon_path):
            self.setIcon(QIcon(icon_path))
            self.setIconSize(QSize(20, 20))
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self._update_style()

    def set_active(self, active: bool):
        self._active = active
        self._update_style()

    def _update_style(self):
        if self._active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: rgba(37, 99, 235, 0.15);
                    border: none;
                    border-left: 3px solid #2563eb;
                    border-radius: 0px;
                    padding: 8px 14px;
                    text-align: left;
                    color: #ffffff;
                    font-size: 13px;
                    font-weight: 600;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    border-left: 3px solid transparent;
                    border-radius: 0px;
                    padding: 8px 14px;
                    text-align: left;
                    color: #7a8ba8;
                    font-size: 13px;
                    font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.04);
                    color: #b8c5d9;
                }
            """)



# ═══════════════════════════════════════════════════════
# FILTERED NOTIFICATIONS PAGE
# Wraps NotificationsPage and adds category filter tabs on top
# ═══════════════════════════════════════════════════════

class FilteredNotificationsPage(QWidget):
    """Adds All / SOS / Alert / Info / System filter tabs above the
    existing NotificationsPage widget from notification.py."""

    TABS = ["All", "SOS", "Alert", "Info", "System"]

    # colour per category: (active-bg hex, active-text hex, border hex)
    _TAB_COLORS = {
        "All":    ("#2563eb", "#ffffff", "#2563eb"),
        "SOS":    ("#3b0000", "#ef4444", "#ef4444"),
        "Alert":  ("#431407", "#f97316", "#f97316"),
        "Info":   ("#172554", "#60a5fa", "#60a5fa"),
        "System": ("#2e1065", "#a78bfa", "#a78bfa"),
    }

    def __init__(self, notif_page: NotificationsPage, parent=None):
        super().__init__(parent)
        self._notif_page = notif_page
        self._active_tab = "All"

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Tab bar ──
        tab_bar = QFrame()
        tab_bar.setFixedHeight(48)
        tab_bar.setStyleSheet("background: transparent; border: none;")
        tab_lay = QHBoxLayout(tab_bar)
        tab_lay.setContentsMargins(12, 8, 12, 4)
        tab_lay.setSpacing(8)

        self._tab_btns: dict[str, QPushButton] = {}
        for t in self.TABS:
            btn = QPushButton(t)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(28)
            self._tab_btns[t] = btn
            btn.clicked.connect(lambda _, tab=t: self._set_tab(tab))
            tab_lay.addWidget(btn)
        tab_lay.addStretch()

        outer.addWidget(tab_bar)
        outer.addWidget(notif_page)

        self._refresh_tab_styles()

    def _set_tab(self, tab: str):
        self._active_tab = tab
        self._refresh_tab_styles()
        # Drive the existing filter_combo on NotificationsPage
        idx = self._notif_page.filter_combo.findText(tab)
        if idx >= 0:
            self._notif_page.filter_combo.setCurrentIndex(idx)

    def _refresh_tab_styles(self):
        for t, btn in self._tab_btns.items():
            active = (t == self._active_tab)
            bg, fg, border = self._TAB_COLORS.get(t, ("#1e2d44", "#64748b", "#334155"))
            if active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {bg};
                        color: {fg};
                        border: 1px solid {border};
                        border-radius: 14px;
                        padding: 3px 14px;
                        font-size: 12px;
                        font-weight: 700;
                    }}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        color: #64748b;
                        border: 1px solid #334155;
                        border-radius: 14px;
                        padding: 3px 14px;
                        font-size: 12px;
                        font-weight: 600;
                    }
                    QPushButton:hover {
                        background-color: rgba(255,255,255,0.04);
                        color: #94a3b8;
                    }
                """)

    def load_notifications(self):
        """Delegates to the inner page and reapplies the current filter."""
        self._notif_page.load_notifications()
        self._set_tab(self._active_tab)


# ═══════════════════════════════════════════════════════
# MAIN WINDOW
# ═══════════════════════════════════════════════════════

class MainWindow(QMainWindow):
    logout_requested = pyqtSignal()

    def __init__(self, user: User):
        super().__init__()
        self.setWindowTitle("SafeTrack")
        self.setMinimumSize(1200, 700)
        self.user = user

        self.port = "COM9"
        self.hrs = 48
        monitor = Simulate(self.port, self.hrs)
        monitor.start()

        self.setStyleSheet("QMainWindow { background-color: #060a13; }")

        # ═════ CENTRAL WIDGET ═════
        central = QWidget()
        self.setCentralWidget(central)
        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # ═══════════════════════════════════════════
        # SIDEBAR
        # ═══════════════════════════════════════════
        sidebar = QFrame()
        sidebar.setFixedWidth(220)
        sidebar.setStyleSheet("""
            QFrame {
                background-color: #0b1120;
                border-right: 1px solid #141e30;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # ── Logo ──
        logo_frame = QFrame()
        logo_frame.setFixedHeight(64)
        logo_frame.setStyleSheet("background: transparent; border: none; border-bottom: 1px solid #141e30;")
        logo_lay = QHBoxLayout(logo_frame)
        logo_lay.setContentsMargins(20, 0, 20, 0)

        logo_text = QLabel("SafeTrack")
        logo_text.setStyleSheet("""
            color: #ffffff; font-size: 17px; font-weight: 700;
            letter-spacing: 0.5px; border: none;
        """)
        logo_lay.addWidget(logo_text)
        logo_lay.addStretch()
        sidebar_layout.addWidget(logo_frame)

        # ── Section label ──
        nav_label = QLabel("NAVIGATION")
        nav_label.setStyleSheet("""
            color: #3d4f68; font-size: 10px; font-weight: 700;
            letter-spacing: 1.5px; padding: 18px 20px 8px 20px; border: none;
        """)
        sidebar_layout.addWidget(nav_label)

        # ── Nav buttons ──
        img = lambda name: os.path.join("images", name)

        self.sidebar_buttons_info = [
            ("btnMap",           "Map",           img("map_icon.png")),
            ("btnNotifications", "Notifications", img("notifications_icon.png")),
            ("btnHistory",       "History & Logs",img("history_icon.png")),
            ("btnSettings",      "Settings",      img("settings.png")),
        ]
        if user.is_admin:
            self.sidebar_buttons_info.append(("btnInvite", "Invite", img("settings.png")))

        self.sidebar_buttons = {}
        for obj_name, label, icon_path in self.sidebar_buttons_info:
            btn = SidebarButton(f"  {label}", icon_path)
            sidebar_layout.addWidget(btn)
            self.sidebar_buttons[obj_name] = btn
            btn.clicked.connect(lambda checked, n=obj_name: self.on_sidebar_button(n))

        self.sidebar_buttons["btnMap"].set_active(True)
        self._active_btn = "btnMap"

        sidebar_layout.addStretch()

        # ── Divider ──
        div = QFrame()
        div.setFixedHeight(1)
        div.setStyleSheet("background-color: #141e30; border: none;")
        sidebar_layout.addWidget(div)

        # ── Logout (separate, bottom) ──
        logout_btn = SidebarButton(f"  Logout", img("logout_icon.png"))
        logout_btn.setStyleSheet("""
            QPushButton {
                background: transparent; border: none;
                border-left: 3px solid transparent;
                padding: 8px 14px; text-align: left;
                color: #5a6a82; font-size: 13px; font-weight: 500;
            }
            QPushButton:hover {
                background-color: rgba(239, 68, 68, 0.08);
                color: #ef4444;
            }
        """)
        logout_btn.clicked.connect(lambda: self.on_sidebar_button("btnLogout"))
        self.sidebar_buttons["btnLogout"] = logout_btn
        sidebar_layout.addWidget(logout_btn)

        # ── User profile (clickable → Settings > Account) ──
        user_frame = QFrame()
        user_frame.setFixedHeight(66)
        user_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        user_frame.setStyleSheet("""
            QFrame {
                background-color: rgba(255,255,255,0.02);
                border: none; border-top: 1px solid #141e30;
            }
            QFrame:hover {
                background-color: rgba(37,99,235,0.08);
            }
        """)
        user_lay = QHBoxLayout(user_frame)
        user_lay.setContentsMargins(16, 0, 16, 0)
        user_lay.setSpacing(10)

        display_name = user.fullname if user.fullname else user.username
        parts = display_name.split()
        initials = (parts[0][0] + (parts[1][0] if len(parts) > 1 else "")) if parts else "?"
        avatar = AvatarWidget(initials, 36)
        user_lay.addWidget(avatar)

        user_text = QVBoxLayout()
        user_text.setSpacing(1)
        user_text.setContentsMargins(0, 0, 0, 0)

        name_lbl = QLabel(display_name)
        name_lbl.setStyleSheet("color: #cfd8e8; font-size: 13px; font-weight: 600; border: none;")
        role_lbl = QLabel("Admin" if user.is_admin else "User")
        role_lbl.setStyleSheet("color: #4a5a72; font-size: 11px; font-weight: 500; border: none;")

        user_text.addStretch()
        user_text.addWidget(name_lbl)
        user_text.addWidget(role_lbl)
        user_text.addStretch()
        user_lay.addLayout(user_text)
        user_lay.addStretch()
        sidebar_layout.addWidget(user_frame)

        # Make the profile strip open Settings > Account when clicked
        user_frame.mousePressEvent = lambda e: self.on_sidebar_button("btnSettings")

        root_layout.addWidget(sidebar)

        # ═══════════════════════════════════════════
        # MAIN CONTENT AREA
        # ═══════════════════════════════════════════
        main_area = QWidget()
        main_area.setStyleSheet("""
            QWidget {
                background-color: #060a13;
                color: #cfd8e8;
            }
        """)
        main_layout = QVBoxLayout(main_area)
        main_layout.setContentsMargins(20, 16, 20, 16)
        main_layout.setSpacing(0)
        root_layout.addWidget(main_area)

        content_layout = QHBoxLayout()
        content_layout.setSpacing(0)
        main_layout.addLayout(content_layout)

        self.stacked_layout = QStackedLayout()
        content_frame = QFrame()
        content_frame.setStyleSheet("background: transparent; border: none;")
        content_frame.setLayout(self.stacked_layout)
        content_layout.addWidget(content_frame)

        self.blank_pages = {}

        # Backend worker
        self.backend = BackendWorker(user)
        self.backend.notification_signal.connect(self.handle_backend_notification)
        self.backend.start()

        # ── MAP PAGE ──
        self.alert_system = AlertSystem(self, user)
        self.alert_system.viewNodeRequested.connect(self.open_node_on_map)

        self.center = (33.42057834806449, -111.9322007773111)
        self.map_widget = MapDisplay(center_coord=self.center, user=user)
        self.stacked_layout.addWidget(self.map_widget)

        # ── NOTIFICATIONS PAGE (wrapped with category filter tabs) ──
        _inner_notif = NotificationsPage(user=user)
        _inner_notif.load_notifications()
        self.notifications_page = FilteredNotificationsPage(_inner_notif)
        self.stacked_layout.addWidget(self.notifications_page)  # index 1

        # ── HISTORY PAGE (placeholder until history.py is integrated) ──
        history_page = QFrame()
        history_page.setStyleSheet("background: transparent;")
        h_layout = QVBoxLayout(history_page)
        h_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_icon = QLabel("📋")
        h_icon.setStyleSheet("font-size: 48px; color: #1e2d44;")
        h_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(h_icon)
        h_title = QLabel("History & Logs")
        h_title.setStyleSheet("font-size: 22px; font-weight: 600; color: #2a3a52;")
        h_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(h_title)
        h_sub = QLabel("Share history.py to complete this page")
        h_sub.setStyleSheet("font-size: 13px; color: #1e2d44;")
        h_sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        h_layout.addWidget(h_sub)
        self.stacked_layout.addWidget(history_page)             # index 2
        self.blank_pages["btnHistory"] = history_page

        # ── SETTINGS PAGE ──
        self.settings_page = SettingsPage(user=user)
        self.settings_page.back_requested.connect(
            lambda: self.on_sidebar_button("btnMap")
        )
        self.stacked_layout.addWidget(self.settings_page)       # index 3
        self.blank_pages["btnSettings"] = self.settings_page

        # ── BLANK PAGES (Invite, etc.) ──
        # btnMap=0, btnNotifications=1, btnHistory=2, btnSettings=3 already set
        _skip = {"btnMap", "btnNotifications", "btnHistory", "btnSettings"}
        for obj_name, label, _ in self.sidebar_buttons_info:
            if obj_name in _skip:
                continue
            page = QFrame()
            page.setStyleSheet("background: transparent;")
            p_layout = QVBoxLayout(page)
            p_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

            icon_lbl = QLabel("⚙")
            icon_lbl.setStyleSheet("font-size: 48px; color: #1e2d44;")
            icon_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            p_layout.addWidget(icon_lbl)

            title_lbl = QLabel(label)
            title_lbl.setStyleSheet("font-size: 22px; font-weight: 600; color: #2a3a52;")
            title_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            p_layout.addWidget(title_lbl)

            sub_lbl = QLabel("Coming soon")
            sub_lbl.setStyleSheet("font-size: 13px; color: #1e2d44;")
            sub_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            p_layout.addWidget(sub_lbl)

            self.stacked_layout.addWidget(page)
            self.blank_pages[obj_name] = page

        self.stacked_layout.setCurrentIndex(0)

    # ─────────────────────────────────────
    # SIDEBAR NAVIGATION
    # ─────────────────────────────────────

    def _set_active(self, name: str):
        for key, btn in self.sidebar_buttons.items():
            if key == "btnLogout":
                continue
            if isinstance(btn, SidebarButton):
                btn.set_active(key == name)
        self._active_btn = name

    def on_sidebar_button(self, name):
        match name:
            case "btnMap":
                self._set_active(name)
                self.stacked_layout.setCurrentIndex(0)
                self.map_widget.update_map()
            case "btnNotifications":
                self._set_active(name)
                self.stacked_layout.setCurrentIndex(1)
                self.notifications_page.load_notifications()
            case "btnHistory":
                self._set_active(name)
                page_widget = self.blank_pages.get("btnHistory")
                if page_widget is not None:
                    idx = self.stacked_layout.indexOf(page_widget)
                    if idx != -1:
                        self.stacked_layout.setCurrentIndex(idx)
            case "btnSettings":
                self._set_active(name)
                self.settings_page.show_section("Account")
                idx = self.stacked_layout.indexOf(self.settings_page)
                if idx != -1:
                    self.stacked_layout.setCurrentIndex(idx)
            case "btnInvite":
                self._generate_invite()
            case "btnLogout":
                self.logout_requested.emit()
                self.close()
            case _:
                self._set_active(name)
                page_widget = self.blank_pages.get(name)
                if page_widget is not None:
                    idx = self.stacked_layout.indexOf(page_widget)
                    if idx != -1:
                        self.stacked_layout.setCurrentIndex(idx)

    def _generate_invite(self):
        if not self.user.is_admin:
            QMessageBox.warning(self, "Permission Denied",
                                "Only admins can create invite codes.")
            return
        code = adb.create_invite_code(self.user.username)
        QMessageBox.information(
            self, "Invite Code Generated",
            f"Share this code with the person you want to invite:\n\n"
            f"    {code}\n\n"
            f"It expires in 48 hours and can only be used once."
        )

    # ─────────────────────────────────────
    # BACKEND / MAP HANDLERS
    # ─────────────────────────────────────

    def node_added_callback(self, node_id):
        self.map_widget.update_map()

    def handle_backend_notification(self, notif):
        if notif[2] == "SOS":
            self.alert_system.show_alert_node(notif)
        if self.stacked_layout.currentWidget() == self.map_widget:
            self.map_widget.update_map()

    def closeEvent(self, event):
        if hasattr(self, "backend"):
            try:
                self.backend.requestInterruption()
                self.backend.wait(2000)
            except Exception:
                pass
        super().closeEvent(event)

    def open_node_on_map(self, node_id):
        self.stacked_layout.setCurrentIndex(0)
        self._set_active("btnMap")
        self.map_widget.center_on_node(node_id)


# ═══════════════════════════════════════════════════════
# ENTRY POINT
# ═══════════════════════════════════════════════════════

if __name__ == "__main__":
    database.init_db()
    database.init_notif_db()
    database.init_user_db()
    adb.init_auth_db()

    app = QApplication(sys.argv)
    login_window = LoginWindow()
    main_window = None

    def start_main(user):
        global main_window
        main_window = MainWindow(user)
        main_window.logout_requested.connect(show_login)
        login_window.hide()
        main_window.show()
        print(f"Logged in: {user.list_info()}")

    def show_login():
        login_window.show()

    login_window.login_successful.connect(start_main)
    login_window.show()
    sys.exit(app.exec())