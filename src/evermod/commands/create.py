import json, shutil, re
from pathlib import Path
from evermod.utils.paths import get_templates_dir, get_versions_file

def run(name: str, mc_version: str, target_path: str = "."):
    cwd = Path(".").resolve()  # Donde se ejecuta el comando
    target_base = Path(target_path).resolve()  # Donde se creará el mod
    templates = get_templates_dir()
    versions_path = get_versions_file()

    if not versions_path.exists():
        print("❌ 'versions.json' not found in templatesMDK/")
        return

    versions = json.loads(versions_path.read_text(encoding="utf-8"))

    if mc_version not in versions:
        print(f"❌ Unsupported Minecraft version: {mc_version}")
        print("Available versions:")
        for v in versions.keys():
            print(f"  - Minecraft {v}")
        print()
        print("💡 Usage: evermod create <mod_name> [minecraft_version] [target_path]")
        print("💡 Example: evermod create SilentMask 1.19.2 ./mods")
        return

    # Detect workspace in the current directory (not in the target path)
    settings_path = cwd / "settings.gradle"
    is_workspace = settings_path.exists()

    mod_dir = target_base / name
    if mod_dir.exists():
        print(f"⚠️  A folder named '{name}' already exists in {target_base}")
        return

    mod_dir.mkdir(parents=True, exist_ok=True)
    version_info = versions[mc_version]

    shutil.copy(templates / version_info["template"], mod_dir / "build.gradle")
    shutil.copy(templates / "gradle.properties.template", mod_dir / "gradle.properties")

    properties_path = mod_dir / "gradle.properties"

    # === Detect Forge systemProp configuration ===
    major, minor, patch = (mc_version.split(".") + ["0", "0"])[:3]
    use_system_prop = False
    if major == "1" and int(minor) >= 22:
        use_system_prop = True
    elif major == "1" and minor == "21" and int(patch) >= 4:
        use_system_prop = True

    sys_block = ""
    if use_system_prop:
        sys_block = (
            "\n\n# Gradle recompilation settings\n"
            "systemProp.net.minecraftforge.gradle.repo.recompile.fork=true\n"
            "systemProp.net.minecraftforge.gradle.repo.recompile.fork.args=-Xmx5G\n\n"
            "# Disable automatic repository injection by ForgeGradle\n"
            "systemProp.net.minecraftforge.gradle.repo.attach=false\n\n"
        )

    text = properties_path.read_text(encoding="utf-8")

    # Replace markers
    text = re.sub(r"\[systemProp\]", sys_block, text)
    replacements = {
        r"\[mcv\]": mc_version,
        r"\[mcvr\]": version_info["minecraft_version_range"],
        r"\[fv\]": version_info["forge_version"],
        r"\[fm\]": version_info["forge_version_mayor"],
        r"\[mid\]": name,
    }
    for k, v in replacements.items():
        text = re.sub(k, v, text)
    properties_path.write_text(text, encoding="utf-8")

    # Register mod in workspace if detected
    if is_workspace:
        relative_path = mod_dir.relative_to(cwd)
        include_path = str(relative_path).replace("\\", ":").replace("/", ":")
        include_line = f'include("{include_path}")'

        content = settings_path.read_text(encoding="utf-8")
        if include_line not in content:
            with open(settings_path, "a", encoding="utf-8") as f:
                f.write(f"\n{include_line}\n")
            print(f"🧩 Mod '{name}' registered in workspace settings.gradle")
        else:
            print(f"ℹ️  Mod '{name}' is already registered in workspace.")

    print(f"✅ Mod '{name}' created successfully for Minecraft {mc_version} (Forge {version_info['forge_version']})")
    print(f"📂 Location: {mod_dir}")
    print(f"🏗️ Workspace mode: {'ON' if is_workspace else 'OFF'}")
