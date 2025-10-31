import sys
from pathlib import Path

def get_global_dir() -> Path:
    """
    Returns the global EverMod configuration directory.
    Example:
      Windows → C:\\Users\\<user>\\.evermod
      Linux/macOS → /home/<user>/.evermod
    """
    base = Path.home() / ".evermod"
    base.mkdir(parents=True, exist_ok=True)
    return base

def get_templates_dir() -> Path:
    """Returns the path to the global Forge templates directory."""
    templates = get_global_dir() / "templatesMDK"
    templates.mkdir(parents=True, exist_ok=True)
    return templates

def get_versions_file() -> Path:
    """Returns the versions.json file inside the global templates folder."""
    return get_templates_dir() / "versions.json"

def get_manifest_path() -> Path:
    """Find manifest.json dynamically whether running from source or compiled .exe."""
    if getattr(sys, 'frozen', False):
        base_path = Path(sys._MEIPASS)
    else:
        base_path = Path(__file__).resolve()
        for parent in base_path.parents:
            candidate = parent / "manifest.json"
            if candidate.exists():
                return candidate
        base_path = Path.cwd()
    return base_path / "manifest.json"