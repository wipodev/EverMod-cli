import re

def ask(prompt, default=None):
    """Input helper with default value."""
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default

def sanitize_string(s: str) -> str:
    """Sanitize a string to be used as mod ID or similar identifiers."""
    return re.sub(r'[^a-z0-9_]', '_', s.lower().strip().replace(" ", "_"))

def sanitize_package(s: str) -> str:
    """Sanitize a string for use as a Java package (keep dots)."""
    parts = s.lower().strip().replace(" ", "_").split(".")
    return ".".join(re.sub(r'[^a-z0-9_]', '_', p) for p in parts if p)
