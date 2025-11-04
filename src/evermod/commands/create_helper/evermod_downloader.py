import json, urllib.request, hashlib, zipfile, io
from pathlib import Path

CACHE_DIR = Path.home() / ".evermod" / "cache"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

EVERMOD_LATEST_URL = "https://wipodev.com/EverMod/releases/latest/"

def download_evermod_module(mc_version: str, extract_to: Path):
    """Download and extract the latest EverMod module for a given MC version."""
    try:
        print("\n🌐 Fetching latest EverMod module information...")
        with urllib.request.urlopen(f"{EVERMOD_LATEST_URL}versions.json") as response:
            release_data = json.load(response)

        release_tag = release_data.get("version", "unknown")
        modules = release_data.get("modules", {})

        if not modules:
            print("⚠️  No module data found in release manifest.")
            return

        module_info = modules.get(mc_version)
        if not module_info:
            print(f"⚠️  No EverMod module available for Minecraft {mc_version}.")
            return

        zip_name = Path(module_info["path"]).name
        sha256_expected = module_info["sha256"]
        module_url = f"{EVERMOD_LATEST_URL}{zip_name}"

        cache_zip = CACHE_DIR / zip_name
        if cache_zip.exists():
            print("💾 Using cached EverMod module...")
            data = cache_zip.read_bytes()
        else:
            print(f"⬇️  Downloading EverMod core module for {mc_version}...")
            with urllib.request.urlopen(module_url) as r:
                data = r.read()
            cache_zip.write_bytes(data)

        sha256_actual = hashlib.sha256(data).hexdigest()
        if sha256_actual != sha256_expected:
            print("❌ Checksum mismatch! Removing cached file.")
            cache_zip.unlink(missing_ok=True)
            return

        print("✅ Integrity verified. Extracting EverMod module...")
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            z.extractall(extract_to)
        print(f"📦 EverMod {mc_version} module embedded successfully.")

    except Exception as e:
        print(f"⚠️  Could not fetch or extract EverMod module: {e}")
