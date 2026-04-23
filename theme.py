import json
import os

_THEME_FILE = "theme_pref.json"

_THEMES = {
    "dark": {
        "page_bg": "#060a13",
        "panel_bg": "#0f172b",
        "panel_alt": "#111c34",
        "border": "#1a2540",
        "text": "#f1f5f9",
        "muted": "#94a3b8",
        "soft": "#64748b",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "success": "#22c55e",
        "success_hover": "#16a34a",
        "danger": "#ef4444",
        "danger_hover": "#dc2626",
        "input_bg": "#0d1526",
        "input_border": "#1e2d44",
        "input_focus": "#2563eb",
        "readonly_bg": "#0b1324",
        "nav_hover": "rgba(255,255,255,0.04)",
        "nav_active_bg": "#2563eb",
        "nav_active_text": "#ffffff",
        "card_border": "#22314d",
    },
    "light": {
        "page_bg": "#f5f7fb",
        "panel_bg": "#ffffff",
        "panel_alt": "#f8fafc",
        "border": "#dbe4f0",
        "text": "#0f172a",
        "muted": "#475569",
        "soft": "#64748b",
        "accent": "#2563eb",
        "accent_hover": "#1d4ed8",
        "success": "#16a34a",
        "success_hover": "#15803d",
        "danger": "#dc2626",
        "danger_hover": "#b91c1c",
        "input_bg": "#ffffff",
        "input_border": "#cbd5e1",
        "input_focus": "#2563eb",
        "readonly_bg": "#f8fafc",
        "nav_hover": "#eff6ff",
        "nav_active_bg": "#2563eb",
        "nav_active_text": "#ffffff",
        "card_border": "#dbe4f0",
    },
}


def get_theme(name: str = "dark") -> dict:
    return _THEMES.get(name, _THEMES["dark"]).copy()


def load_theme_name() -> str:
    if not os.path.exists(_THEME_FILE):
        return "dark"

    try:
        with open(_THEME_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        name = data.get("theme", "dark")
        return name if name in _THEMES else "dark"
    except Exception:
        return "dark"


def save_theme_name(name: str) -> None:
    if name not in _THEMES:
        name = "dark"

    with open(_THEME_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": name}, f, indent=2)