import json
from pathlib import Path
from evermod.utils.paths import get_global_dir, get_manifest_path

def show_full_version():
    """Display CLI version, framework compatibility, and templates info."""

    # --- CLI Manifest (local root) ---
    cli_manifest_path = get_manifest_path()
    if not cli_manifest_path.exists():
        print("❌ CLI manifest.json not found.")
        return

    cli_manifest = json.loads(cli_manifest_path.read_text(encoding="utf-8"))
    cli_version = cli_manifest.get("version", "unknown")

    # --- Templates Manifest (global .evermod folder) ---
    global_dir = get_global_dir()
    template_manifest_path = global_dir / "version.json"

    if template_manifest_path.exists():
        template_manifest = json.loads(template_manifest_path.read_text(encoding="utf-8"))
        templates_version = template_manifest.get("version", "not installed")
        templates_date = template_manifest.get("released", "unknown date")
    else:
        templates_version = "not installed"
        templates_date = "—"

    # --- Output summary ---
    print("🧩 EverMod CLI Information")
    print("----------------------------")
    print(f"CLI Version:           v{cli_version}")
    print(f"Installed Templates:   v{templates_version}")
    print(f"Templates Released:    {templates_date}")
    print(f"Global Path:           {global_dir}")
