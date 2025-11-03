import subprocess, os, sys, shutil, json, re
from pathlib import Path
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# =============================================
# 🧩 EverMod CLI — Build Automation Script
# =============================================
# Features:
# - Detects unchanged version and prompts user
# - Syncs manifest.json → setup.iss & pyproject.toml
# - Cleans old builds
# - Builds PyInstaller (onefile)
# - Builds Inno Setup installer
# =============================================

# Paths
ROOT = Path(__file__).resolve().parent
APPDATA = os.environ["LOCALAPPDATA"]
DIST = ROOT / "dist"
SPEC = ROOT / "evermod.spec"
SETUP_ISS = ROOT / "setup.iss"
MANIFEST = ROOT / "manifest.json"
PYPROJECT = ROOT / "pyproject.toml"
INNO_SETUP_EXE = Path(APPDATA) / "Programs/Inno Setup 6/ISCC.exe"

# -----------------------------------------
# 🔐 Optional key generation before build
# -----------------------------------------
def generate_keys():
    """Run generate_keys.py before building."""
    print("\n🔐 Generating EverMod RSA keys...\n")

    private_path = Path.home() / ".evermod" / "keys" / "private.pem"
    public_path = Path("src/evermod/auth/keys/evermod_public.pem")
    public_path.parent.mkdir(parents=True, exist_ok=True)
    private_path.parent.mkdir(parents=True, exist_ok=True)

    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    with open(private_path, "wb") as f:
        f.write(
            private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=serialization.NoEncryption()
            )
        )

    public_key = private_key.public_key()
    with open(public_path, "wb") as f:
        f.write(
            public_key.public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
        )

    print(f"✅ Claves generadas correctamente:\n - {private_path}\n - {public_path}")

# -----------------------------------------
# 🧠 Utilities
# -----------------------------------------
def run_command(cmd: list[str], cwd: Path = ROOT):
    """Run a system command and stream output."""
    print(f"\n> {' '.join(cmd)}\n")
    process = subprocess.Popen(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    for line in process.stdout:
        print(line, end="")
    process.wait()
    if process.returncode != 0:
        print(f"\n❌ Command failed with exit code {process.returncode}")
        sys.exit(process.returncode)

# -----------------------------------------
# 🔄 Synchronization + Validation
# -----------------------------------------
def sync_versions():
    """Sync version from manifest.json → setup.iss & pyproject.toml, ask if unchanged."""
    if not MANIFEST.exists():
        print("❌ manifest.json not found.")
        sys.exit(1)

    manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
    version = manifest.get("version", "").strip()
    if not version:
        print("❌ Version not found in manifest.json.")
        sys.exit(1)

    # Get last recorded version (if any) from setup.iss
    last_version = None
    if SETUP_ISS.exists():
        setup_text = SETUP_ISS.read_text(encoding="utf-8")
        match = re.search(r"(?m)^AppVersion=(.*)", setup_text)
        if match:
            last_version = match.group(1).strip()

    if last_version and last_version == version:
        print(f"\n ⚠️  The version number in manifest.json ({version}) has not changed since last build.")
        choice = input("Do you want to keep this version? (y/n): ").strip().lower()
        if choice not in ("y", "yes"):
            new_version = input("Enter new version number (current: " + version + "): ").strip()
            if new_version:
                manifest["version"] = new_version
                version = new_version
                MANIFEST.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
                print(f"✅ Updated manifest.json → version {version}")
            else:
                print("❌ No new version entered. Aborting.")
                sys.exit(1)

    print(f"\n🔄 Syncing version {version} across project files...\n")

    # --- Update setup.iss ---
    if not SETUP_ISS.exists():
        print("❌ setup.iss not found.")
        sys.exit(1)

    setup_text = SETUP_ISS.read_text(encoding="utf-8")
    setup_text = re.sub(r"(?m)^AppVersion=.*", f"AppVersion={version}", setup_text)
    SETUP_ISS.write_text(setup_text, encoding="utf-8")
    print(f"✅ setup.iss updated → AppVersion={version}")

    # --- Update pyproject.toml ---
    if PYPROJECT.exists():
        py_text = PYPROJECT.read_text(encoding="utf-8")
        py_text = re.sub(r'(?m)^version\s*=\s*".*"', f'version = "{version}"', py_text)
        PYPROJECT.write_text(py_text, encoding="utf-8")
        print(f"✅ pyproject.toml updated → version = {version}")
    else:
        print("⚠️ pyproject.toml not found (skipped).")

    print()
    return version

# -----------------------------------------
# 🧹 Clean previous builds
# -----------------------------------------
def clean_previous_builds():
    """Step 0: Remove previous build artifacts."""
    print("\n🧹 Cleaning previous build artifacts...\n")
    for folder in ("build", "dist", "__pycache__"):
        folder_path = ROOT / folder
        if folder_path.exists():
            shutil.rmtree(folder_path)
            print(f"  🗑️  Removed {folder_path}")
    # Also remove the old Inno Setup output if exists
    output_dir = ROOT / "Output"
    if output_dir.exists():
        shutil.rmtree(output_dir)
        print(f"  🗑️  Removed {output_dir}")

# -----------------------------------------
# 🚀 build
# -----------------------------------------
def build_pyinstaller():
    """Step 1: Build evermod.exe using PyInstaller"""
    print("\n🚀 Building EverMod CLI executable with PyInstaller...\n")

    if not SPEC.exists():
        print("❌ evermod.spec not found. Please create it first.")
        sys.exit(1)

    cmd = ["pyinstaller", str(SPEC), "--noconfirm", "--clean"]
    run_command(cmd)

    dist_exe = DIST / "evermod.exe"
    build_exe = ROOT / "build" / "evermod" / "evermod.exe"

    if dist_exe.exists():
        print(f"\n✅ PyInstaller build completed successfully: {dist_exe}")
    elif build_exe.exists():
        print(f"\n ⚠️  PyInstaller placed the exe in build/. Moving to dist/...")
        DIST.mkdir(parents=True, exist_ok=True)
        import shutil
        shutil.copy(build_exe, dist_exe)
        print(f"✅ Copied {build_exe} → {dist_exe}")
    else:
        print("❌ PyInstaller did not produce evermod.exe")
        print("🔎 Check the 'build' folder manually for output files.")
        sys.exit(1)

def build_inno_setup():
    """Step 2: Build installer using Inno Setup"""
    print("\n📦 Building EverMod installer with Inno Setup...\n")

    if not SETUP_ISS.exists():
        print("❌ setup.iss not found in project root.")
        sys.exit(1)

    if not INNO_SETUP_EXE.exists():
        print("❌ Inno Setup not found. Please update INNO_SETUP_EXE path in build.py.")
        sys.exit(1)

    cmd = [str(INNO_SETUP_EXE), str(SETUP_ISS)]
    run_command(cmd)

    output_dir = ROOT / "Output"
    if output_dir.exists():
        installers = list(output_dir.glob("*.exe"))
        if installers:
            print(f"\n✅ Inno Setup installer created: {installers[0]}")
        else:
            print("⚠️ No installer found in Output folder.")
    else:
        print("⚠️ Output folder not found. Check setup.iss configuration.")

def main():
    print("🧩 EverMod CLI — Build Automation\n")
    args = [a.lower() for a in sys.argv[1:]]
    if "--keys" in args or "keys" in args or "-k" in args:
        generate_keys()
    clean_previous_builds()
    build_pyinstaller()
    build_inno_setup()
    print("\n🎉 Build process completed successfully!\n")

if __name__ == "__main__":
    main()
