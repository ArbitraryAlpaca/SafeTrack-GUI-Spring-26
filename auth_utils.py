"""
auth_utils.py
─────────────
Password hashing (bcrypt), validation helpers, username rules,
invite-code / reset-token generation, and a field-level Fernet
encryption helper for the database.
"""

import re
import os
import secrets
import string


import bcrypt
from cryptography.fernet import Fernet

# ────────────────────────────────────────────
# 1.  FIELD-LEVEL DATABASE ENCRYPTION (Fernet)
# ────────────────────────────────────────────

_KEY_FILE = "safetrack.key"


def _load_or_create_key() -> bytes:
    """Return Fernet key, creating one on first run."""
    if os.path.exists(_KEY_FILE):
        with open(_KEY_FILE, "rb") as f:
            return f.read()
    key = Fernet.generate_key()
    with open(_KEY_FILE, "wb") as f:
        f.write(key)
    return key


_fernet = Fernet(_load_or_create_key())


def encrypt_field(plain: str) -> str:
    """Encrypt a string field → base64 token stored in DB."""
    return _fernet.encrypt(plain.encode()).decode()


def decrypt_field(token: str) -> str:
    """Decrypt a base64 token from DB → original string."""
    return _fernet.decrypt(token.encode()).decode()


# ────────────────────────────────────────────
# 2.  PASSWORD HASHING  (bcrypt)
# ────────────────────────────────────────────

def hash_password(password: str) -> str:
    """Return a bcrypt hash of *password*."""
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


def verify_password(password: str, hashed: str) -> bool:
    """Check *password* against a stored bcrypt *hashed* value."""
    try:
        return bcrypt.checkpw(password.encode(), hashed.encode())
    except Exception:
        return False


# ────────────────────────────────────────────
# 3.  USERNAME VALIDATION
# ────────────────────────────────────────────

_USERNAME_RE = re.compile(r"^[a-zA-Z0-9._-]{3,18}$")

RESERVED_NAMES = frozenset({
    "admin", "administrator", "support", "root", "system",
    "safetrack", "moderator", "mod", "staff", "help",
    "info", "contact", "security", "null", "undefined",
    "test", "postmaster", "webmaster", "localhost",
})


def validate_username(username: str) -> tuple[bool, str]:
    """
    Return (ok, message).  Rules:
      • 3-18 ASCII chars  (letters, digits, . _ -)
      • Not a reserved name
    """
    if not username:
        return False, "Username is required."
    if not _USERNAME_RE.match(username):
        return False, "Username must be 3–18 characters (letters, digits, . _ - only)."
    if username.lower() in RESERVED_NAMES:
        return False, "That username is reserved."
    return True, ""


# ────────────────────────────────────────────
# 4.  PASSWORD VALIDATION
# ────────────────────────────────────────────

# Top common passwords (trimmed list – extend as needed)
COMMON_PASSWORDS = frozenset({
    "password", "123456", "12345678", "qwerty", "abc123",
    "monkey", "1234567", "letmein", "trustno1", "dragon",
    "baseball", "iloveyou", "master", "sunshine", "ashley",
    "bailey", "shadow", "123456789", "1234567890", "password1",
    "password123", "qwerty123", "1q2w3e4r", "qwertyuiop",
    "admin", "welcome", "football", "charlie", "donald",
    "passw0rd", "p@ssword", "p@ssw0rd", "changeme",
    "000000", "111111", "121212", "654321", "666666",
    "696969", "123123", "000000", "mustang", "access",
    "michael", "jordan", "jennifer", "hunter", "thomas",
    "internet", "soccer", "pepper", "summer", "starwars",
    "whatever", "batman", "superman", "hello", "trustme",
    "letmein1", "welcome1", "master1", "p@ssword1", "google",
    "linkedin", "princess", "flower", "cookie", "computer",
    "samantha", "jessica", "ginger", "december", "november",
})


def validate_password(password: str, username: str = "") -> tuple[bool, str]:
    """
    Return (ok, message).  Policy:
      • 8–12 characters
      • Spaces allowed (passphrases)
      • Must not be in common-password list
      • Must not contain the username or 'safetrack' (case-insensitive)
      • No forced complexity / no forced resets
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters."
    if len(password) > 12:
        return False, "Password must be 12 characters or fewer."

    lower = password.lower()
    if lower.replace(" ", "") in COMMON_PASSWORDS:
        return False, "That password is too common. Choose something unique."

    if username and username.lower() in lower:
        return False, "Password must not contain your username."

    if "safetrack" in lower:
        return False, "Password must not contain the app name."

    # Reject trivially repetitive strings (e.g. "aaaaaaaaaaaaaa")
    if len(set(password.replace(" ", ""))) < 4:
        return False, "Password is too simple – use more variety."

    return True, ""


# ────────────────────────────────────────────
# 5.  EMAIL VALIDATION (lightweight)
# ────────────────────────────────────────────

_EMAIL_RE = re.compile(
    r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
)


def validate_email(email: str) -> tuple[bool, str]:
    if not email:
        return False, "Email is required."
    if not _EMAIL_RE.match(email):
        return False, "Enter a valid email address."
    return True, ""


# ────────────────────────────────────────────
# 6.  TOKEN / INVITE CODE GENERATION
# ────────────────────────────────────────────

def generate_reset_token() -> str:
    """URL-safe 48-char token for password-reset links."""
    return secrets.token_urlsafe(36)


def generate_invite_code() -> str:
    """8-char uppercase alphanumeric invite code."""
    alphabet = string.ascii_uppercase + string.digits
    return "".join(secrets.choice(alphabet) for _ in range(8))


# ────────────────────────────────────────────
# 7.  FULL-NAME VALIDATION
# ────────────────────────────────────────────

def validate_fullname(name: str) -> tuple[bool, str]:
    if not name or len(name.strip()) < 2:
        return False, "Full name must be at least 2 characters."
    if len(name) > 100:
        return False, "Full name is too long."
    if not re.match(r"^[a-zA-Z\s\-'.]+$", name):
        return False, "Full name can only contain letters, spaces, hyphens, and apostrophes."
    return True, ""