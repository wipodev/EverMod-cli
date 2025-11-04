import json, shutil, tempfile, subprocess, urllib.request
from pathlib import Path
from packaging import version
from evermod.utils.paths import get_global_dir, get_templates_dir

MANIFEST_URL = "https://raw.githubusercontent.com/wipodev/evermod-templates/main/manifest.json"
REPO_URL = "https://github.com/wipodev/evermod-templates.git"

def run(force: bool = False, silent: bool = False):
    global_dir = get_global_dir()
    templates_dir = get_templates_dir()
    local_manifest_path = global_dir / "version.json"

    if not silent:
        print("🔍 Checking for EverMod template updates...")

    # === Fetch remote manifest ===
    try:
        with urllib.request.urlopen(MANIFEST_URL) as response:
            remote_manifest = json.load(response)
    except Exception as e:
        if not silent:
            print(f"❌ Unable to read remote manifest: {e}")
        return

    remote_version = remote_manifest.get("version", "0.0.0")
    local_version = "0.0.0"

    if local_manifest_path.exists():
        try:
            local_data = json.loads(local_manifest_path.read_text(encoding="utf-8"))
            local_version = local_data.get("version", "0.0.0")
        except Exception:
            pass

    remote_v = version.parse(remote_version)
    local_v = version.parse(local_version)

    # === Skip if already up to date ===
    if not force and remote_v <= local_v:
        if not silent:
            print(f"✅ Templates are already up to date (v{local_version}).")
            print("ℹ️  Use '--force' to reinstall templates anyway.")
        return

    # === Show changelog if interactive ===
    if not silent:
        print(f"🆕 New version available: v{remote_version} (current v{local_version})")
        print(f"📅 Released: {remote_manifest.get('released', 'unknown date')}")
        print("\n📋 Changelog:")
        for line in remote_manifest.get("changelog", []):
            print(f"  • {line}")
        print()

        confirm = input("Would you like to update your local templates? (y/n): ").strip().lower()
        if confirm != "y":
            print("❎ Update cancelled.")
            return

    # === Clone and replace templates ===
    with tempfile.TemporaryDirectory() as tmp:
        tmp_path = Path(tmp)
        if not silent:
            print("⬇️  Downloading new templates...")

        try:
            subprocess.run(
                ["git", "clone", "--depth", "1", REPO_URL, str(tmp_path)],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True
            )
        except subprocess.CalledProcessError:
            if not silent:
                print("❌ Failed to clone the repository.")
            return

        remote_templates = tmp_path / "templates"
        if not remote_templates.exists():
            if not silent:
                print("❌ Remote repository does not contain 'templates' folder.")
            return

        if templates_dir.exists():
            shutil.rmtree(templates_dir)
        shutil.copytree(remote_templates, templates_dir)

        local_manifest_path.write_text(
            json.dumps(remote_manifest, indent=2), encoding="utf-8"
        )

        if not silent:
            print(f"✅ Templates updated successfully to version v{remote_version}.")
            print(f"📁 Location: {templates_dir}")
