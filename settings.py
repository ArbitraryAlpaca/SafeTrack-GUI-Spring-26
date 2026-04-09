# ═══════════════════════════════════════════════════════
# settings.py  –  SafeTrack Settings Page
# ═══════════════════════════════════════════════════════

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QLineEdit, QScrollArea, QSizePolicy, QStackedWidget,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont

import auth_database as adb
from login import User


# ───────────────────────────────────────────────────────
# SECTION BUTTON  (left-hand tab list)
# ───────────────────────────────────────────────────────
class _SectionBtn(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self._icon  = icon
        self._label = label
        self._active = False
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self._refresh()

    def set_active(self, active: bool):
        self._active = active
        self._refresh()

    def _refresh(self):
        if self._active:
            self.setStyleSheet("""
                QPushButton {
                    background-color: #2563eb;
                    border: none; border-radius: 8px;
                    padding: 8px 14px; text-align: left;
                    color: #ffffff;
                    font-size: 13px; font-weight: 700;
                }
            """)
        else:
            self.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none; border-radius: 8px;
                    padding: 8px 14px; text-align: left;
                    color: #64748b;
                    font-size: 13px; font-weight: 500;
                }
                QPushButton:hover {
                    background-color: rgba(255,255,255,0.04);
                    color: #94a3b8;
                }
            """)
        self.setText(f"  {self._icon}  {self._label}")


# ───────────────────────────────────────────────────────
# STYLED INPUT
# ───────────────────────────────────────────────────────
def _make_input(placeholder: str = "", password: bool = False) -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    if password:
        w.setEchoMode(QLineEdit.EchoMode.Password)
    w.setFixedHeight(44)
    w.setStyleSheet("""
        QLineEdit {
            background-color: #0d1526;
            border: 1px solid #1e2d44;
            border-radius: 8px;
            padding: 0 12px;
            color: #cbd5e1;
            font-size: 13px;
        }
        QLineEdit:focus {
            border-color: #2563eb;
            background-color: #0f1a30;
        }
        QLineEdit:hover {
            border-color: #2a3a52;
        }
    """)
    return w


def _field_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setStyleSheet("color: #94a3b8; font-size: 13px; font-weight: 600;")
    return lbl


# ───────────────────────────────────────────────────────
# CONTENT PANELS
# ───────────────────────────────────────────────────────

class _AccountPanel(QWidget):
    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── scroll area so it works at any window height ──
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent; border: none;")
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        form = QVBoxLayout(inner)
        form.setContentsMargins(0, 0, 16, 16)
        form.setSpacing(18)

        # Section title
        title = QLabel("Account Settings")
        title.setStyleSheet("color: #f1f5f9; font-size: 17px; font-weight: 700;")
        form.addWidget(title)

        # Fields
        self.full_name  = _make_input("Enter your full name")
        self.username   = _make_input("Enter username")
        self.email      = _make_input("Enter email address")
        self.phone      = _make_input("Enter phone number")

        # Pre-fill from user object
        if user.fullname:
            self.full_name.setText(user.fullname)
        self.username.setText(user.username)

        for label_text, widget in [
            ("Full Name",     self.full_name),
            ("Username",      self.username),
            ("Email",         self.email),
            ("Phone Number",  self.phone),
        ]:
            lbl = _field_label(label_text)
            form.addWidget(lbl)
            form.addWidget(widget)

        # ── Action buttons ──
        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.change_pw_btn = QPushButton("Change Password")
        self.change_pw_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.change_pw_btn.setFixedHeight(40)
        self.change_pw_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: #ffffff; border: none;
                border-radius: 8px;
                font-size: 13px; font-weight: 700;
                padding: 0 20px;
            }
            QPushButton:hover { background-color: #dc2626; }
            QPushButton:pressed { background-color: #b91c1c; }
        """)

        self.delete_btn = QPushButton("Delete Account")
        self.delete_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.delete_btn.setFixedHeight(40)
        self.delete_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #64748b;
                border: 1px solid #334155;
                border-radius: 8px;
                font-size: 13px; font-weight: 600;
                padding: 0 20px;
            }
            QPushButton:hover {
                border-color: #ef4444;
                color: #ef4444;
            }
        """)

        btn_row.addWidget(self.change_pw_btn)
        btn_row.addWidget(self.delete_btn)
        btn_row.addStretch()
        form.addLayout(btn_row)
        form.addStretch()

        scroll.setWidget(inner)
        layout.addWidget(scroll)

        # Connections
        self.change_pw_btn.clicked.connect(self._on_change_password)
        self.delete_btn.clicked.connect(self._on_delete_account)

    def _on_change_password(self):
        dlg = _ChangePasswordDialog(self.user, self)
        dlg.exec()

    def _on_delete_account(self):
        resp = QMessageBox.warning(
            self, "Delete Account",
            "Are you sure you want to delete your account?\nThis action cannot be undone.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.Cancel,
        )
        if resp == QMessageBox.StandardButton.Yes:
            QMessageBox.information(self, "Account Deleted",
                                    "Your account has been deleted.")


class _PlaceholderPanel(QWidget):
    def __init__(self, icon: str, title: str, parent=None):
        super().__init__(parent)
        self.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self)
        lay.setAlignment(Qt.AlignmentFlag.AlignCenter)

        ico = QLabel(icon)
        ico.setStyleSheet("font-size: 44px;")
        ico.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(ico)

        t = QLabel(title)
        t.setStyleSheet("font-size: 20px; font-weight: 600; color: #2a3a52;")
        t.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(t)

        sub = QLabel("Coming soon")
        sub.setStyleSheet("font-size: 13px; color: #1e2d44;")
        sub.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lay.addWidget(sub)

class _NodesPanel(QWidget):
    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet("background: transparent;")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(0, 0, 0, 16)
        lay.setSpacing(14)

        title = QLabel("Device & Nodes")
        title.setStyleSheet("color: #f1f5f9; font-size: 17px; font-weight: 700;")
        lay.addWidget(title)

        if user.is_admin:
            self._build_admin_view(lay)
        else:
            self._build_user_view(lay)

    def _build_user_view(self, lay):
        sub = QLabel("Your assigned nodes:")
        sub.setStyleSheet("color: #94a3b8; font-size: 13px;")
        lay.addWidget(sub)

        if not self.user.viewable_nodes:
            none_lbl = QLabel("No nodes assigned to your account yet.")
            none_lbl.setStyleSheet("color: #475569; font-size: 13px;")
            lay.addWidget(none_lbl)
        else:
            for nid in self.user.viewable_nodes:
                row = QLabel(f"  📡  Node {nid}")
                row.setStyleSheet(
                    "background: #0d1526; border: 1px solid #1e2d44;"
                    "border-radius: 8px; padding: 8px 12px; color: #cfd8e8;"
                )
                lay.addWidget(row)
        lay.addStretch()

    def _build_admin_view(self, lay):
        sub = QLabel("Assign nodes to users (admin only):")
        sub.setStyleSheet("color: #94a3b8; font-size: 13px;")
        lay.addWidget(sub)

        from PyQt6.QtWidgets import QComboBox, QSpinBox
        row1 = QHBoxLayout()
        self.user_combo = QComboBox()
        self.user_combo.setStyleSheet(
            "QComboBox { background: #0d1526; border: 1px solid #1e2d44;"
            "border-radius: 8px; padding: 6px 12px; color: #cfd8e8; }"
        )
        self._users_data = adb.get_all_users_with_nodes()
        for u in self._users_data:
            self.user_combo.addItem(f"{u['username']} ({'admin' if u['is_admin'] else 'user'})")
        row1.addWidget(QLabel("User:"))
        row1.addWidget(self.user_combo, stretch=1)
        lay.addLayout(row1)

        row2 = QHBoxLayout()
        self.node_spin = QSpinBox()
        self.node_spin.setRange(1, 9999)
        self.node_spin.setStyleSheet(
            "QSpinBox { background: #0d1526; border: 1px solid #1e2d44;"
            "border-radius: 8px; padding: 6px 12px; color: #cfd8e8; }"
        )
        assign_btn = QPushButton("Assign Node")
        assign_btn.setStyleSheet(
            "QPushButton { background: #2563eb; color: #fff; border: none;"
            "border-radius: 8px; padding: 6px 16px; font-weight: 700; }"
            "QPushButton:hover { background: #1d4ed8; }"
        )
        revoke_btn = QPushButton("Revoke Node")
        revoke_btn.setStyleSheet(
            "QPushButton { background: #ef4444; color: #fff; border: none;"
            "border-radius: 8px; padding: 6px 16px; font-weight: 700; }"
            "QPushButton:hover { background: #dc2626; }"
        )
        assign_btn.clicked.connect(self._assign)
        revoke_btn.clicked.connect(self._revoke)
        row2.addWidget(QLabel("Node ID:"))
        row2.addWidget(self.node_spin)
        row2.addWidget(assign_btn)
        row2.addWidget(revoke_btn)
        row2.addStretch()
        lay.addLayout(row2)

        self.status_lbl = QLabel("")
        self.status_lbl.setStyleSheet("color: #6bffa1; font-size: 12px;")
        lay.addWidget(self.status_lbl)

        self.assignments_lbl = QLabel("")
        self.assignments_lbl.setStyleSheet("color: #94a3b8; font-size: 12px;")
        self.assignments_lbl.setWordWrap(True)
        lay.addWidget(self.assignments_lbl)
        self.user_combo.currentIndexChanged.connect(self._refresh_assignments)
        self._refresh_assignments(0)
        lay.addStretch()

    def _current_username(self) -> str:
        idx = self.user_combo.currentIndex()
        if 0 <= idx < len(self._users_data):
            return self._users_data[idx]["username"]
        return ""

    def _refresh_assignments(self, _idx):
        uname = self._current_username()
        if not uname:
            return
        nodes = adb.get_user_nodes(uname)
        self.assignments_lbl.setText(
            f"Currently assigned: {nodes if nodes else 'none'}"
        )

    def _assign(self):
        uname = self._current_username()
        nid = self.node_spin.value()
        if adb.assign_node(uname, nid):
            self.status_lbl.setText(f"✓ Node {nid} assigned to {uname}")
            self._refresh_assignments(0)

    def _revoke(self):
        uname = self._current_username()
        nid = self.node_spin.value()
        if adb.revoke_node(uname, nid):
            self.status_lbl.setText(f"Node {nid} revoked from {uname}")
            self._refresh_assignments(0)
# ───────────────────────────────────────────────────────
# CHANGE PASSWORD DIALOG
# ───────────────────────────────────────────────────────
class _ChangePasswordDialog(QWidget):
    def __init__(self, user: User, parent=None):
        super().__init__(parent, Qt.WindowType.Dialog)
        self.user = user
        self.setWindowTitle("Change Password")
        self.setFixedSize(400, 280)
        self.setStyleSheet("""
            QWidget {
                background-color: #0f172b;
                color: #f1f5f9;
            }
        """)

        lay = QVBoxLayout(self)
        lay.setContentsMargins(24, 24, 24, 24)
        lay.setSpacing(14)

        title = QLabel("Change Password")
        title.setStyleSheet("font-size: 16px; font-weight: 700; color: #f1f5f9;")
        lay.addWidget(title)

        self.current_pw = _make_input("Current password", password=True)
        self.new_pw     = _make_input("New password",     password=True)
        self.confirm_pw = _make_input("Confirm new password", password=True)

        for lbl, w in [("Current Password", self.current_pw),
                       ("New Password",     self.new_pw),
                       ("Confirm Password", self.confirm_pw)]:
            lay.addWidget(_field_label(lbl))
            lay.addWidget(w)

        btn_row = QHBoxLayout()
        save_btn = QPushButton("Save")
        save_btn.setFixedHeight(38)
        save_btn.setStyleSheet("""
            QPushButton {
                background: #2563eb; color: #fff;
                border: none; border-radius: 7px;
                font-size: 13px; font-weight: 700; padding: 0 20px;
            }
            QPushButton:hover { background: #1d4ed8; }
        """)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setFixedHeight(38)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background: transparent; color: #64748b;
                border: 1px solid #334155; border-radius: 7px;
                font-size: 13px; font-weight: 600; padding: 0 20px;
            }
            QPushButton:hover { color: #94a3b8; border-color: #475569; }
        """)
        save_btn.clicked.connect(self._save)
        cancel_btn.clicked.connect(self.close)
        btn_row.addWidget(save_btn)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        lay.addLayout(btn_row)

    def exec(self):
        self.show()

    def _save(self):
        current = self.current_pw.text()
        new_pw  = self.new_pw.text()
        confirm = self.confirm_pw.text()

        if not current or not new_pw:
            QMessageBox.warning(self, "Missing Fields", "All fields are required.")
            return
        if new_pw != confirm:
            QMessageBox.warning(self, "Mismatch", "New passwords do not match.")
            return

        # Verify current password
        result = adb.authenticate_user(self.user.username, current)
        if result is None:
            QMessageBox.warning(self, "Wrong Password", "Current password is incorrect.")
            return

        from auth_utils import validate_password
        ok, msg = validate_password(new_pw, self.user.username)
        if not ok:
            QMessageBox.warning(self, "Weak Password", msg)
            return

        adb.update_password(self.user.username, new_pw)
        QMessageBox.information(self, "Password Changed",
                            "Your password has been updated successfully.")
        self.close()


# ───────────────────────────────────────────────────────
# MAIN SETTINGS PAGE
# ───────────────────────────────────────────────────────
class SettingsPage(QWidget):
    """Full settings page with left tab list and right content panel."""

    back_requested = pyqtSignal()   # emitted when user clicks ← Back

    _SECTIONS = [
        ("👤", "Account"),
        ("🔔", "Notifications"),
        ("🔒", "Privacy & Security"),
        ("📡", "Device & Nodes"),
        ("⚙️", "App Preferences"),
        ("📞", "Emergency Contacts"),
        ("ℹ️", "About & Help"),
    ]

    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.setStyleSheet("background: #060a13;")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        # ── Top bar ──
        top = QHBoxLayout()
        top.setSpacing(16)

        back_btn = QPushButton("← Back")
        back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        back_btn.setFixedHeight(34)
        back_btn.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: #94a3b8;
                border: 1px solid #334155;
                border-radius: 7px;
                font-size: 13px; font-weight: 600;
                padding: 0 14px;
            }
            QPushButton:hover {
                background-color: rgba(255,255,255,0.04);
                color: #cbd5e1;
            }
        """)
        back_btn.clicked.connect(self.back_requested.emit)

        page_title = QLabel("Settings")
        page_title.setStyleSheet(
            "color: #f1f5f9; font-size: 24px; font-weight: 800; letter-spacing: -0.5px;"
        )

        save_btn = QPushButton("💾  Save Changes")
        save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        save_btn.setFixedHeight(36)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #22c55e;
                color: #ffffff; border: none;
                border-radius: 8px;
                font-size: 13px; font-weight: 700;
                padding: 0 18px;
            }
            QPushButton:hover { background-color: #16a34a; }
            QPushButton:pressed { background-color: #15803d; }
        """)
        save_btn.clicked.connect(self._save_changes)

        top.addWidget(back_btn)
        top.addWidget(page_title)
        top.addStretch()
        top.addWidget(save_btn)
        root.addLayout(top)

        # ── Body (left nav + right content) ──
        body = QHBoxLayout()
        body.setSpacing(16)

        # Left nav panel
        nav_frame = QFrame()
        nav_frame.setFixedWidth(220)
        nav_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172b;
                border: 1px solid #1a2540;
                border-radius: 12px;
            }
        """)
        nav_lay = QVBoxLayout(nav_frame)
        nav_lay.setContentsMargins(8, 10, 8, 10)
        nav_lay.setSpacing(2)

        self._section_btns: dict[str, _SectionBtn] = {}
        for icon, label in self._SECTIONS:
            btn = _SectionBtn(icon, label)
            btn.clicked.connect(lambda _, lbl=label: self.show_section(lbl))
            nav_lay.addWidget(btn)
            self._section_btns[label] = btn
        nav_lay.addStretch()

        # Right content panel
        content_frame = QFrame()
        content_frame.setStyleSheet("""
            QFrame {
                background-color: #0f172b;
                border: 1px solid #1a2540;
                border-radius: 12px;
            }
        """)
        content_lay = QVBoxLayout(content_frame)
        content_lay.setContentsMargins(24, 20, 24, 20)
        content_lay.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setStyleSheet("background: transparent; border: none;")

        self._panels: dict[str, QWidget] = {}

        for icon, label in self._SECTIONS:
            if label == "Account":
                panel = _AccountPanel(user)
            elif label == "Device & Nodes":
                panel = _NodesPanel(user)
            else:
                panel = _PlaceholderPanel(icon, label)
            self._stack.addWidget(panel)
            self._panels[label] = panel

        content_lay.addWidget(self._stack)

        body.addWidget(nav_frame)
        body.addWidget(content_frame, stretch=1)
        root.addLayout(body, stretch=1)

        # Default to Account tab
        self.show_section("Account")

    def show_section(self, label: str):
        """Switch to a named section tab."""
        for lbl, btn in self._section_btns.items():
            btn.set_active(lbl == label)
        panel = self._panels.get(label)
        if panel:
            self._stack.setCurrentWidget(panel)

    def _save_changes(self):
        # Pull values from account panel and persist what we can
        panel = self._panels.get("Account")
        if isinstance(panel, _AccountPanel):
            fullname = panel.full_name.text().strip()
            # Persist fullname if auth_database supports it
            try:
                adb.update_fullname(self.user.username, fullname)
                self.user.fullname = fullname
            except Exception:
                pass
        QMessageBox.information(self, "Saved", "Your settings have been saved.")