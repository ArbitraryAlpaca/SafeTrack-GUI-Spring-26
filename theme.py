from dataclasses import dataclass
from PyQt6.QtCore import QSettings
from PyQt6.QtGui import QFont

ORG = "SafeTrack"
APP = "SafeTrackGUI"
KEY_THEME = "appearance/theme"  # "dark" or "light"

@dataclass(frozen=True)
class Theme:
    name: str
    sidebar_bg: str
    page_bg: str
    text: str
    hover: str
    border: str
    notification: str

DARK = Theme(
    name="dark",
    sidebar_bg="#0b1220",
    page_bg="#070b14",
    text="#cfd8ff",
    hover="#162040",
    border="#2b3a4a",
    notification="#0f1724"
)

LIGHT = Theme(
    name="light",
    sidebar_bg="#ffffff",
    page_bg="#f5f7fb",
    text="#0b1220",
    hover="#e7eef9",
    border="#cfd8dc",
    notification="#99aec3"
)

def get_theme(name: str) -> Theme:
    return LIGHT if str(name).lower() == "light" else DARK

def load_theme_name() -> str:
    s = QSettings(ORG, APP)
    return str(s.value(KEY_THEME, "dark"))

def save_theme_name(name: str) -> None:
    s = QSettings(ORG, APP)
    s.setValue(KEY_THEME, name)

def sidebar_qss(t: Theme) -> str:
    return f"""
    QFrame {{
        background-color: {t.sidebar_bg};
        color: {t.text};
    }}
    QPushButton {{
        background: transparent;
        border: 1px solid rgba(0,0,0,0.08);
        padding: 8px;
        text-align: left;
        color: {t.text};
        border-radius: 6px;
        margin-bottom: 6px;
    }}
    QPushButton:hover {{
        background-color: {t.hover};
    }}
    """

def main_area_qss(t: Theme) -> str:
    return f"background-color: {t.page_bg}; color: {t.text};"