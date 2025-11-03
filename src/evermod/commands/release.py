import hashlib, json, shutil, os
from datetime import date
from pathlib import Path
from evermod.auth.security import require_internal_auth, sign_file
from evermod.utils.publisher import publish_release, create_main_tag, is_prerelease

def run(release_tag: str, publish: bool, auto: bool = False, target: str = "."):
    require_internal_auth(f"release:{release_tag}")

    ROOT = Path(target).resolve()
    FRAMEWORK = ROOT / "framework"
    RELEASE_ROOT = ROOT / "releases"
    RELEASE_DIR = RELEASE_ROOT / release_tag

    # --- Clean up old releases folder if exists ---
    if RELEASE_DIR.exists():
        print(f"🧹 Cleaning previous release folder: {RELEASE_DIR}")
        shutil.rmtree(RELEASE_DIR)
    RELEASE_DIR.mkdir(parents=True, exist_ok=True)

    print(f"\n🚀 Starting EverMod release build: {release_tag}\n")

    if not FRAMEWORK.exists():
        print("❌ Folder 'framework/' not found. Aborting.")
        return

    modules = sorted([p for p in FRAMEWORK.iterdir() if p.is_dir() and p.name.startswith("evermod-")])
    if not modules:
        print("⚠️  No modules found under 'framework/'. Nothing to release.")
        return
    
    # --- Determine status (stable, beta, alpha, rc) ---
    prerelease = is_prerelease(release_tag)
    if "alpha" in release_tag.lower():
        status = "alpha"
    elif "beta" in release_tag.lower():
        status = "beta"
    elif any(x in release_tag.lower() for x in ["rc", "release_candidate"]):
        status = "rc"
    else:
        status = "stable"

    # --- Base structure for this version ---
    release_info = {
        "schema": 1,
        "version": release_tag,
        "status": status,
        "date": str(date.today()),
        "modules": {},
        "workspace": {}
    }

    # ------------------------------------------------------------
    # 📦 1. Compress each module (evermod-{version}.zip)
    # ------------------------------------------------------------
    for module in modules:
        version = module.name.replace("evermod-", "")
        net_path = module / "src" / "main" / "java" / "net"
        if not net_path.exists():
            print(f"⚠️ Skipped {module.name}: no 'src/main/java/net/' directory.")
            continue

        zip_name = f"evermod-{version}.zip"
        zip_path = RELEASE_DIR / zip_name

        # Copy only 'net' folder into a temp location to zip cleanly
        temp_dir = RELEASE_DIR / f"_temp_{version}"
        if temp_dir.exists():
            shutil.rmtree(temp_dir)
        shutil.copytree(net_path, temp_dir / "net")

        shutil.make_archive(str(zip_path).replace(".zip", ""), "zip", temp_dir)
        shutil.rmtree(temp_dir)

        size_kb = f"{zip_path.stat().st_size // 1024}KB"
        sha256 = hashlib.sha256(zip_path.read_bytes()).hexdigest()

        release_info["modules"][version] = {
            "path": str(zip_path.relative_to(ROOT)).replace("\\", "/"),
            "size": size_kb,
            "sha256": sha256
        }

        print(f"✅ Compressed {zip_name} ({size_kb})")

    # ------------------------------------------------------------
    # 🧩 2. Create full framework workspace zip
    # ------------------------------------------------------------
    framework_zip = RELEASE_DIR / "evermod-framework.zip"
    temp_framework = RELEASE_DIR / "_workspace"

    print("\n🧩 Creating EverMod full framework package...")

    if temp_framework.exists():
        shutil.rmtree(temp_framework)
    temp_framework.mkdir(parents=True)

    # Define files and folders to include
    include_items = [
        ".vscode",
        "framework",
        "gradle",
        "mods",
        ".gitattributes",
        ".gitignore",
        "build.gradle",
        "gradle.properties",
        "gradlew",
        "gradlew.bat",
        "settings.gradle",
        "LICENSE",
        "README.md",
    ]

    for item in include_items:
        src = ROOT / item
        dst = temp_framework / item
        if not src.exists():
            print(f"⚠️  Missing {item}, skipped.")
            continue
        if src.is_dir():
            # Special case: framework folder → exclude all /build directories
            if item == "framework":
                print("📁 Copying framework (excluding build folders)...")
                for root_dir, dirs, files in os.walk(src):
                    if "build" in dirs:
                        dirs.remove("build")  # exclude build/
                    rel_path = Path(root_dir).relative_to(ROOT)
                    target_dir = temp_framework / rel_path
                    target_dir.mkdir(parents=True, exist_ok=True)
                    for f in files:
                        shutil.copy2(Path(root_dir) / f, target_dir / f)
            else:
                shutil.copytree(src, dst)
        else:
            shutil.copy2(src, dst)

    # Compress workspace package
    shutil.make_archive(str(framework_zip).replace(".zip", ""), "zip", temp_framework)
    shutil.rmtree(temp_framework)

    size_kb = f"{framework_zip.stat().st_size // 1024}KB"
    sha256 = hashlib.sha256(framework_zip.read_bytes()).hexdigest()
    release_info["workspace"] = {
        "path": str(framework_zip.relative_to(ROOT)).replace("\\", "/"),
        "size": size_kb,
        "sha256": sha256
    }

    print(f"✅ Created evermod-framework.zip ({size_kb})")

    # ------------------------------------------------------------
    # 🧾 3. Write versions.json and sign
    # ------------------------------------------------------------
    versions_json = RELEASE_DIR / "versions.json"
    versions_json.write_text(json.dumps(release_info, indent=2), encoding="utf-8")
    print(f"\n🧾 versions.json generated → {versions_json}")

    # --- Sign file ---
    sign_file(versions_json)

    # ------------------------------------------------------------
    # 🚀 4. Publish release (optional)
    # ------------------------------------------------------------
    if publish:
        publish_release(release_tag, RELEASE_DIR)

    # --- Create main tag ---
    create_main_tag(release_tag, auto)

    print("\n🎉 EverMod release build completed successfully!\n")
