import json, re, shutil
from pathlib import Path
from jinja2 import Template
from evermod.utils.paths import get_templates_dir, get_versions_file
from evermod.utils.gradle_tools import refresh_environment

def _sanitize_string(s: str) -> str:
    """Sanitize a string to be used as mod ID or similar identifiers."""
    return re.sub(r'[^a-z0-9_]', '_', s.lower().strip().replace(" ", "_"))

def _sanitize_package(s: str) -> str:
    """Sanitize a string for use as a Java package (keep dots)."""
    parts = s.lower().strip().replace(" ", "_").split(".")
    return ".".join(re.sub(r'[^a-z0-9_]', '_', p) for p in parts if p)

def _ask(prompt, default=None):
    """Input helper with default value"""
    value = input(f"{prompt} [{default}]: ").strip()
    return value or default

def run():
    """Interactive mod creation wizard"""
    print("🧩 EverMod — Mod creation wizard")
    print("--------------------------------")

    # === Load versions file ===
    versions_path = get_versions_file()
    if not versions_path.exists():
        print("❌ 'versions.json' not found in templates/")
        return
    versions = json.loads(versions_path.read_text(encoding="utf-8"))

    # === Ask for mod name ===
    mod_name = _ask("Mod name", "NewMod")

    # === Generate mod_id suggestion ===
    suggested_modid = _sanitize_string(mod_name)
    mod_id = _ask("Mod ID", suggested_modid)
    mod_id = _sanitize_string(mod_id)

    # === Ask Minecraft version ===
    print("\nAvailable Minecraft versions:")
    for v in versions.keys():
        print(f" - {v}")
    mc_version = _ask("Select Minecraft version", list(versions.keys())[-1])

    if mc_version not in versions:
        print(f"❌ Unsupported version: {mc_version}")
        return
    version_info = versions[mc_version]

    # === Ask for author and group ===
    author = _ask("Author name", "WipoDev")

    # === Suggest package name ===
    safe_author = _sanitize_string(author)
    package_default = f"net.{safe_author}.{mod_id}"
    package_response = _ask("Package name", package_default).strip()
    package_response = _sanitize_package(package_response)
    package_name = package_response
    package_parts = package_response.split(".")

    # === Target folder ===
    target_base = Path(_ask("Target directory", ".")).resolve()
    mod_dir = target_base / mod_name
    if mod_dir.exists():
        print(f"⚠️ Folder '{mod_name}' already exists in {target_base}")
        return
    mod_dir.mkdir(parents=True, exist_ok=True)

    # === Create src structure ===
    src_main_java = mod_dir / "src" / "main" / "java" / Path(*package_parts)
    src_main_resources = mod_dir / "src" / "main" / "resources"
    src_main_metainf = mod_dir / "src" / "main" / "resources" / "META-INF"
    src_main_java.mkdir(parents=True, exist_ok=True)
    src_main_resources.mkdir(parents=True, exist_ok=True)
    src_main_metainf.mkdir(parents=True, exist_ok=True)
    templates_dir = get_templates_dir()

    # === Copy template files ===
    for tpl_file, dst_file in [
        ("mods.toml", src_main_resources / "mods.toml"),
        ("pack.mcmeta", src_main_metainf / "pack.mcmeta"),
        ("LICENSE.txt", mod_dir / "LICENSE.txt"),
    ]:
        tpl_path = templates_dir / tpl_file
        shutil.copy2(tpl_path, dst_file)

    # === Detect workspace (settings.gradle en el cwd) ===
    cwd = Path(".").resolve()
    settings_path = cwd / "settings.gradle"
    is_workspace = settings_path.exists()

    # === Templates ===
    build_tpl = templates_dir / "build.gradle.j2"
    props_tpl = templates_dir / "gradle.properties.j2"
    main_tpl = templates_dir / "MainMod.java.j2"

    # === Render context ===
    context = version_info.copy()
    context.update({
        "minecraft_version": mc_version,
        "mod_id": mod_id,
        "mod_group": safe_author,
        "mod_name": mod_name,
        "mod_authors": author,
        "package_name": package_name,
    })

    # === Render templates ===
    for tpl, output in [
        (build_tpl, mod_dir / "build.gradle"),
        (props_tpl, mod_dir / "gradle.properties"),
        (main_tpl, src_main_java / "MainMod.java"),
    ]:
        with open(tpl, encoding="utf-8") as f:
            t = Template(f.read())
        result = t.render(context)
        output.write_text(result, encoding="utf-8")

    # === Registrar en workspace si aplica ===
    if is_workspace:
        relative_path = mod_dir.relative_to(cwd)
        include_path = str(relative_path).replace("\\", ":").replace("/", ":")
        include_line = f'include("{include_path}")'

        content = settings_path.read_text(encoding="utf-8")
        if include_line not in content:
            with open(settings_path, "a", encoding="utf-8") as f:
                f.write(f"\n{include_line}\n")
            print(f"🧩 Mod '{mod_name}' registered in workspace settings.gradle")
        else:
            print(f"ℹ️ Mod '{mod_name}' is already registered in workspace.")
    else:
        # === create gradle wrapper structure ===
        gradle_dir = mod_dir / "gradle" / "wrapper"
        gradle_dir.mkdir(parents=True, exist_ok=True)

        # === Copy template files ===
        for tpl_file, dst_file in [
            (".gitignore", mod_dir / ".gitignore"),
            (".gitattributes", mod_dir / ".gitattributes"),
            ("gradlew", mod_dir / "gradlew"),
            ("gradlew.bat", mod_dir / "gradlew.bat"),
            ("settings.gradle", mod_dir / "settings.gradle"),
            ("gradle/wrapper/gradle-wrapper.jar", gradle_dir / "gradle-wrapper.jar"),
            ("gradle/wrapper/gradle-wrapper.properties", gradle_dir / "gradle-wrapper.properties"),
        ]:
            tpl_path = templates_dir / tpl_file
            shutil.copy2(tpl_path, dst_file)

    print(f"\n✅ Mod '{mod_name}' created successfully!")
    print(f"📦 Minecraft {mc_version} (Forge {version_info['forge_version']})")
    print(f"📂 Location: {mod_dir}")
    print(f"🏗️ Workspace mode: {'ON' if is_workspace else 'OFF'}")
    print("--------------------------------")

    refresh_environment()
