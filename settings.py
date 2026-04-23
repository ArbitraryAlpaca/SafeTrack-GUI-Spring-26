from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QFrame, QLineEdit, QStackedWidget, QMessageBox, QDialog,
    QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal
import auth_database as adb
from login import User
import theme


class _SectionBtn(QPushButton):
    def __init__(self, icon: str, label: str, parent=None):
        super().__init__(parent)
        self._icon = icon
        self._label = label
        self._active = False
        self._theme_name = "dark"
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(42)
        self._refresh()

    def set_active(self, active: bool):
        self._active = active
        self._refresh()

    def set_theme(self, theme_name: str):
        self._theme_name = theme_name
        self._refresh()

    def _refresh(self):
        t = theme.get_theme(self._theme_name)

        if self._active:
            self.setStyleSheet(f"""
                QPushButton {{
                    background-color: {t["nav_active_bg"]};
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    text-align: left;
                    color: {t["nav_active_text"]};
                    font-size: 13px;
                    font-weight: 700;
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QPushButton {{
                    background: transparent;
                    border: none;
                    border-radius: 8px;
                    padding: 8px 14px;
                    text-align: left;
                    color: {t["soft"]};
                    font-size: 13px;
                    font-weight: 500;
                }}
                QPushButton:hover {{
                    background-color: {t["nav_hover"]};
                    color: {t["text"]};
                }}
            """)

        self.setText(f"  {self._icon}  {self._label}")


def _field_label(text: str, theme_name: str) -> QLabel:
    lbl = QLabel(text)
    t = theme.get_theme(theme_name)
    lbl.setStyleSheet(
        f"color: {t['muted']}; font-size: 13px; font-weight: 600;"
    )
    return lbl


def _make_input(placeholder: str = "", read_only: bool = False) -> QLineEdit:
    w = QLineEdit()
    w.setPlaceholderText(placeholder)
    w.setFixedHeight(44)
    w.setReadOnly(read_only)
    return w


def _apply_input_style(widget: QLineEdit, theme_name: str, read_only: bool = False):
    t = theme.get_theme(theme_name)

    if read_only:
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {t["readonly_bg"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
                padding: 0 12px;
                color: {t["muted"]};
                font-size: 13px;
            }}
        """)
    else:
        widget.setStyleSheet(f"""
            QLineEdit {{
                background-color: {t["input_bg"]};
                border: 1px solid {t["input_border"]};
                border-radius: 8px;
                padding: 0 12px;
                color: {t["text"]};
                font-size: 13px;
            }}
            QLineEdit:focus {{
                border-color: {t["input_focus"]};
            }}
        """)


class _ChangePasswordDialog(QDialog):
    def __init__(self, user: User, theme_name: str, parent=None):
        super().__init__(parent)
        self.user = user
        self.theme_name = theme_name
        self.setWindowTitle("Change Password")
        self.setFixedSize(420, 300)

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(24, 24, 24, 24)
        self.layout.setSpacing(12)

        self.title = QLabel("Change Password")
        self.layout.addWidget(self.title)

        self.current_pw_lbl = QLabel("Current Password")
        self.current_pw = _make_input("Enter current password")
        self.current_pw.setEchoMode(QLineEdit.EchoMode.Password)

        self.new_pw_lbl = QLabel("New Password")
        self.new_pw = _make_input("Enter new password")
        self.new_pw.setEchoMode(QLineEdit.EchoMode.Password)

        self.confirm_pw_lbl = QLabel("Confirm New Password")
        self.confirm_pw = _make_input("Confirm new password")
        self.confirm_pw.setEchoMode(QLineEdit.EchoMode.Password)

        for lbl, field in [
            (self.current_pw_lbl, self.current_pw),
            (self.new_pw_lbl, self.new_pw),
            (self.confirm_pw_lbl, self.confirm_pw),
        ]:
            self.layout.addWidget(lbl)
            self.layout.addWidget(field)

        btn_row = QHBoxLayout()
        self.save_btn = QPushButton("Save")
        self.cancel_btn = QPushButton("Cancel")
        btn_row.addWidget(self.save_btn)
        btn_row.addWidget(self.cancel_btn)
        btn_row.addStretch()
        self.layout.addLayout(btn_row)

        self.save_btn.clicked.connect(self._save)
        self.cancel_btn.clicked.connect(self.reject)

        self.apply_theme(theme_name)

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name
        t = theme.get_theme(theme_name)

        self.setStyleSheet(f"""
            QDialog {{
                background-color: {t["panel_bg"]};
                color: {t["text"]};
            }}
        """)

        self.title.setStyleSheet(
            f"font-size: 16px; font-weight: 700; color: {t['text']};"
        )

        for lbl in [self.current_pw_lbl, self.new_pw_lbl, self.confirm_pw_lbl]:
            lbl.setStyleSheet(f"color: {t['muted']}; font-size: 13px; font-weight: 600;")

        _apply_input_style(self.current_pw, theme_name, read_only=False)
        _apply_input_style(self.new_pw, theme_name, read_only=False)
        _apply_input_style(self.confirm_pw, theme_name, read_only=False)

        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background: {t["accent"]};
                color: white;
                border: none;
                border-radius: 7px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {t["accent_hover"]};
            }}
        """)

        self.cancel_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {t["soft"]};
                border: 1px solid {t["border"]};
                border-radius: 7px;
                padding: 10px 18px;
                font-size: 13px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {t["text"]};
            }}
        """)

    def _save(self):
        current_pw = self.current_pw.text()
        new_pw = self.new_pw.text()
        confirm_pw = self.confirm_pw.text()

        if not current_pw or not new_pw or not confirm_pw:
            QMessageBox.warning(self, "Missing Fields", "Please fill in all password fields.")
            return

        if new_pw != confirm_pw:
            QMessageBox.warning(self, "Mismatch", "New passwords do not match.")
            return

        auth = adb.authenticate_user(self.user.username, current_pw)
        if auth is None:
            QMessageBox.warning(self, "Incorrect Password", "Your current password is incorrect.")
            return

        if adb.update_password(self.user.username, new_pw):
            QMessageBox.information(self, "Password Updated", "Your password was changed successfully.")
            self.accept()
        else:
            QMessageBox.warning(self, "Update Failed", "Could not update the password.")


class _AccountPanel(QWidget):
    def __init__(self, user: User, theme_name: str, parent=None):
        super().__init__(parent)
        self.user = user
        self.theme_name = theme_name
        self.setStyleSheet("background: transparent;")

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet("""
            QScrollArea {
                background: transparent;
                border: none;
            }
        """)

        inner = QWidget()
        inner.setStyleSheet("background: transparent;")
        self.form = QVBoxLayout(inner)
        self.form.setContentsMargins(0, 0, 8, 8)
        self.form.setSpacing(16)

        self.title = QLabel("Account Settings")
        self.form.addWidget(self.title)

        self.full_name_lbl = _field_label("Full Name", theme_name)
        self.full_name = _make_input("Enter your full name")
        self.full_name.setText(user.fullname or "")

        self.username_lbl = _field_label("Username", theme_name)
        self.username = _make_input("", read_only=True)
        self.username.setText(user.username)

        self.email_lbl = _field_label("Email", theme_name)
        self.email = _make_input("", read_only=True)
        self.email.setText(user.email if user.email else "Not set")

        self.phone_lbl = _field_label("Phone Number", theme_name)
        self.phone = _make_input("", read_only=True)
        self.phone.setText("Future field")

        for lbl, field in [
            (self.full_name_lbl, self.full_name),
            (self.username_lbl, self.username),
            (self.email_lbl, self.email),
            (self.phone_lbl, self.phone),
        ]:
            self.form.addWidget(lbl)
            self.form.addWidget(field)

        btn_row = QHBoxLayout()
        btn_row.setSpacing(10)

        self.change_pw_btn = QPushButton("Change Password")
        btn_row.addWidget(self.change_pw_btn)

        btn_row.addStretch()
        self.form.addLayout(btn_row)
        self.form.addStretch()

        scroll.setWidget(inner)
        root.addWidget(scroll)

        self.change_pw_btn.clicked.connect(self._change_password)
        self.apply_theme(theme_name)

    def _change_password(self):
        dlg = _ChangePasswordDialog(self.user, self.theme_name, self)
        dlg.exec()

    def current_fullname(self) -> str:
        return self.full_name.text().strip()

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name
        t = theme.get_theme(theme_name)

        self.setStyleSheet("background: transparent;")
        self.title.setStyleSheet(
            f"color: {t['text']}; font-size: 18px; font-weight: 700;"
        )

        for lbl in [self.full_name_lbl, self.username_lbl, self.email_lbl, self.phone_lbl]:
            lbl.setStyleSheet(f"color: {t['muted']}; font-size: 13px; font-weight: 600;")

        _apply_input_style(self.full_name, theme_name, read_only=False)
        _apply_input_style(self.username, theme_name, read_only=True)
        _apply_input_style(self.email, theme_name, read_only=True)
        _apply_input_style(self.phone, theme_name, read_only=True)

        self.change_pw_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t["danger"]};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 10px 18px;
            }}
            QPushButton:hover {{
                background-color: {t["danger_hover"]};
            }}
        """)


class _PreferencesPanel(QWidget):
    theme_selected = pyqtSignal(str)

    def __init__(self, theme_name: str, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(16)

        self.title = QLabel("App Preferences")
        self.desc = QLabel(
            "Choose the visual mode for the settings page. "
            "This preference is saved locally and will be reused the next time the app opens."
        )
        self.desc.setWordWrap(True)

        self.mode_label = QLabel("Appearance")

        self.btn_row = QHBoxLayout()
        self.btn_row.setSpacing(10)

        self.light_btn = QPushButton("Light Mode")
        self.dark_btn = QPushButton("Dark Mode")

        for btn, name in [(self.light_btn, "light"), (self.dark_btn, "dark")]:
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setFixedHeight(42)
            btn.clicked.connect(lambda _, n=name: self.theme_selected.emit(n))
            self.btn_row.addWidget(btn)

        self.status = QLabel("")
        self.status.setWordWrap(True)

        layout.addWidget(self.title)
        layout.addWidget(self.desc)
        layout.addSpacing(8)
        layout.addWidget(self.mode_label)
        layout.addLayout(self.btn_row)
        layout.addSpacing(8)
        layout.addWidget(self.status)
        layout.addStretch()

        self.apply_theme(theme_name)

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name
        t = theme.get_theme(theme_name)

        self.title.setStyleSheet(
            f"color: {t['text']}; font-size: 18px; font-weight: 700;"
        )
        self.desc.setStyleSheet(
            f"color: {t['muted']}; font-size: 13px; line-height: 1.5;"
        )
        self.mode_label.setStyleSheet(
            f"color: {t['muted']}; font-size: 13px; font-weight: 600;"
        )
        self.status.setStyleSheet(
            f"color: {t['soft']}; font-size: 12px;"
        )

        def style_mode_btn(btn: QPushButton, active: bool):
            if active:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t["accent"]};
                        color: white;
                        border: none;
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 700;
                        padding: 10px 16px;
                    }}
                    QPushButton:hover {{
                        background-color: {t["accent_hover"]};
                    }}
                """)
            else:
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: {t["panel_alt"]};
                        color: {t["text"]};
                        border: 1px solid {t["border"]};
                        border-radius: 8px;
                        font-size: 13px;
                        font-weight: 600;
                        padding: 10px 16px;
                    }}
                    QPushButton:hover {{
                        border-color: {t["accent"]};
                    }}
                """)

        style_mode_btn(self.light_btn, theme_name == "light")
        style_mode_btn(self.dark_btn, theme_name == "dark")
        self.status.setText(f"Current mode: {theme_name.title()}")


class _AboutPanel(QWidget):
    def __init__(self, theme_name: str, parent=None):
        super().__init__(parent)
        self.theme_name = theme_name
        self.setStyleSheet("background: transparent;")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)

        self.title = QLabel("About & Help")
        self.subtitle = QLabel(
            "Support and a brief overview of the SafeTrack project."
        )
        self.subtitle.setWordWrap(True)

        self.support_card = QFrame()
        support_layout = QVBoxLayout(self.support_card)
        support_layout.setContentsMargins(16, 16, 16, 16)
        support_layout.setSpacing(8)

        self.support_title = QLabel("Support")
        self.support_email = QLabel("epics@asu.edu")
        self.meeting_time = QLabel("Meeting Time: Wednesday 7:00–8:15 pm")

        support_layout.addWidget(self.support_title)
        support_layout.addWidget(self.support_email)
        support_layout.addWidget(self.meeting_time)

        self.about_card = QFrame()
        about_layout = QVBoxLayout(self.about_card)
        about_layout.setContentsMargins(16, 16, 16, 16)
        about_layout.setSpacing(8)

        self.about_title = QLabel("How SafeTrack Works")
        self.about_body = QLabel(
            "SafeTrack is designed to help vulnerable people stay connected to their "
            "families and communities while traveling to essential resources. The system "
            "uses a DIY cellular-style mesh built from nodes that communicate over LoRa "
            "radio frequencies. By passing location data across nearby nodes, SafeTrack "
            "can share GPS location, alert loved ones when movement appears suspicious, "
            "and support emergency response workflows."
        )
        self.about_body.setWordWrap(True)

        about_layout.addWidget(self.about_title)
        about_layout.addWidget(self.about_body)

        layout.addWidget(self.title)
        layout.addWidget(self.subtitle)
        layout.addWidget(self.support_card)
        layout.addWidget(self.about_card)
        layout.addStretch()

        self.apply_theme(theme_name)

    def apply_theme(self, theme_name: str):
        self.theme_name = theme_name
        t = theme.get_theme(theme_name)

        self.title.setStyleSheet(
            f"color: {t['text']}; font-size: 18px; font-weight: 700;"
        )
        self.subtitle.setStyleSheet(
            f"color: {t['muted']}; font-size: 13px;"
        )

        for card in [self.support_card, self.about_card]:
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: {t["panel_alt"]};
                    border: 1px solid {t["card_border"]};
                    border-radius: 12px;
                }}
            """)

        self.support_title.setStyleSheet(
            f"color: {t['text']}; font-size: 15px; font-weight: 700;"
        )
        self.support_email.setStyleSheet(
            f"color: {t['accent']}; font-size: 13px; font-weight: 600;"
        )
        self.meeting_time.setStyleSheet(
            f"color: {t['muted']}; font-size: 13px;"
        )

        self.about_title.setStyleSheet(
            f"color: {t['text']}; font-size: 15px; font-weight: 700;"
        )
        self.about_body.setStyleSheet(
            f"color: {t['muted']}; font-size: 13px; line-height: 1.5;"
        )


class SettingsPage(QWidget):
    back_requested = pyqtSignal()
    theme_changed = pyqtSignal(str)

    _SECTIONS = [
        ("👤", "Account"),
        ("🎨", "App Preferences"),
        ("ℹ️", "About & Help"),
    ]

    def __init__(self, user: User, parent=None):
        super().__init__(parent)
        self.user = user
        self.theme_name = theme.load_theme_name()
        self.setObjectName("settingsRoot")

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 20, 24, 20)
        root.setSpacing(20)

        top = QHBoxLayout()
        top.setSpacing(16)

        self.back_btn = QPushButton("← Back")
        self.back_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.back_btn.setFixedHeight(34)
        self.back_btn.clicked.connect(self.back_requested.emit)

        self.page_title = QLabel("Settings")

        self.save_btn = QPushButton("Save Changes")
        self.save_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.save_btn.setFixedHeight(36)
        self.save_btn.clicked.connect(self._save_changes)

        top.addWidget(self.back_btn)
        top.addWidget(self.page_title)
        top.addStretch()
        top.addWidget(self.save_btn)
        root.addLayout(top)

        body = QHBoxLayout()
        body.setSpacing(16)

        self.nav_frame = QFrame()
        self.nav_frame.setObjectName("settingsNavFrame")
        self.nav_frame.setFixedWidth(220)
        nav_lay = QVBoxLayout(self.nav_frame)
        nav_lay.setContentsMargins(8, 10, 8, 10)
        nav_lay.setSpacing(2)

        self._section_btns = {}
        for icon, label in self._SECTIONS:
            btn = _SectionBtn(icon, label)
            btn.clicked.connect(lambda _, lbl=label: self.show_section(lbl))
            nav_lay.addWidget(btn)
            self._section_btns[label] = btn
        nav_lay.addStretch()

        self.content_frame = QFrame()
        self.content_frame.setObjectName("settingsContentFrame")
        content_lay = QVBoxLayout(self.content_frame)
        content_lay.setContentsMargins(24, 20, 24, 20)
        content_lay.setSpacing(0)

        self._stack = QStackedWidget()
        self._stack.setObjectName("settingsStack")
        self._stack.setStyleSheet("background: transparent; border: none;")

        self.account_panel = _AccountPanel(user, self.theme_name)
        self.preferences_panel = _PreferencesPanel(self.theme_name)
        self.about_panel = _AboutPanel(self.theme_name)

        self.preferences_panel.theme_selected.connect(self._on_theme_selected)

        self._panels = {
            "Account": self.account_panel,
            "App Preferences": self.preferences_panel,
            "About & Help": self.about_panel,
        }

        for label in ["Account", "App Preferences", "About & Help"]:
            self._stack.addWidget(self._panels[label])

        content_lay.addWidget(self._stack)

        body.addWidget(self.nav_frame)
        body.addWidget(self.content_frame, stretch=1)
        root.addLayout(body, stretch=1)

        self.show_section("Account")
        self.apply_theme()

    def show_section(self, label: str):
        for lbl, btn in self._section_btns.items():
            btn.set_active(lbl == label)

        panel = self._panels.get(label)
        if panel:
            self._stack.setCurrentWidget(panel)

        self.save_btn.setVisible(label == "Account")

    def _on_theme_selected(self, theme_name: str):
        self.theme_name = theme_name
        theme.save_theme_name(theme_name)
        self.apply_theme()
        self.theme_changed.emit(theme_name)

    def _save_changes(self):
        fullname = self.account_panel.current_fullname()

        if not fullname:
            QMessageBox.warning(self, "Missing Name", "Full name cannot be empty.")
            return

        if fullname == (self.user.fullname or ""):
            QMessageBox.information(self, "No Changes", "Nothing to save.")
            return

        ok = adb.update_fullname(self.user.username, fullname)
        if ok:
            self.user.fullname = fullname
            QMessageBox.information(self, "Saved", "Your profile changes were saved.")
        else:
            QMessageBox.warning(self, "Save Failed", "Could not save your full name.")

    def apply_theme(self):
        t = theme.get_theme(self.theme_name)

        self.setStyleSheet(f"""
            QWidget#settingsRoot {{
                background-color: {t["page_bg"]};
            }}

            QFrame#settingsNavFrame {{
                background-color: {t["panel_bg"]};
                border: 1px solid {t["border"]};
                border-radius: 12px;
            }}

            QFrame#settingsContentFrame {{
                background-color: {t["panel_bg"]};
                border: 1px solid {t["border"]};
                border-radius: 12px;
            }}

            QStackedWidget#settingsStack {{
                background: transparent;
                border: none;
            }}
        """)

        self.page_title.setStyleSheet(
            f"color: {t['text']}; font-size: 24px; font-weight: 800;"
        )

        self.back_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                color: {t["muted"]};
                border: 1px solid {t["border"]};
                border-radius: 7px;
                font-size: 13px;
                font-weight: 600;
                padding: 0 14px;
            }}
            QPushButton:hover {{
                color: {t["text"]};
                background-color: {t["nav_hover"]};
            }}
        """)

        self.save_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {t["success"]};
                color: #ffffff;
                border: none;
                border-radius: 8px;
                font-size: 13px;
                font-weight: 700;
                padding: 0 18px;
            }}
            QPushButton:hover {{
                background-color: {t["success_hover"]};
            }}
        """)

        for btn in self._section_btns.values():
            btn.set_theme(self.theme_name)

        self.account_panel.apply_theme(self.theme_name)
        self.preferences_panel.apply_theme(self.theme_name)
        self.about_panel.apply_theme(self.theme_name)

        self.update()
        self.nav_frame.update()
        self.content_frame.update()
        self._stack.update()