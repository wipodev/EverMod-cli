import json, shutil
from pathlib import Path
from evermod.utils.paths import get_versions_file
from evermod.utils.gradle_tools import refresh_environment
from evermod.commands.create_helper.io_utils import ask, sanitize_string, sanitize_package
from evermod.commands.create_helper.template_utils import render_template
from evermod.commands.create_helper.structure_builder import create_mod_structure
from evermod.commands.create_helper.evermod_downloader import download_evermod_module

def run():
    print("🧩 EverMod — Mod creation wizard")
    print("--------------------------------")

    versions_path = get_versions_file()
    if not versions_path.exists():
        print("❌ 'versions.json' not found in templates/")
        return
    versions = json.loads(versions_path.read_text(encoding="utf-8"))

    mod_name = ask("Mod name", "NewMod")
    suggested_modid = sanitize_string(mod_name)
    mod_id = sanitize_string(ask("Mod ID", suggested_modid))
    print("\nAvailable Minecraft versions:")
    for v in versions.keys(): print(f" - {v}")
    mc_version = ask("Select Minecraft version", list(versions.keys())[0])
    if mc_version not in versions:
        print(f"❌ Unsupported version: {mc_version}")
        return

    version_info = versions[mc_version]
    author = ask("Author name", "WipoDev")
    safe_author = sanitize_string(author)
    package_default = f"net.{safe_author}.{mod_id}"
    package_name = sanitize_package(ask("Package name", package_default))
    package_parts = package_name.split(".")

    target_base = Path(ask("Target directory", ".")).resolve()
    mod_dir = target_base / mod_name
    if mod_dir.exists():
        print(f"⚠️ Folder '{mod_name}' already exists in {target_base}")
        return
    mod_dir.mkdir(parents=True, exist_ok=True)

    templates_dir, src_main_java, src_main_java_mod, src_main_resources = create_mod_structure(mod_dir, package_parts)

    context = version_info.copy()
    context.update({
        "minecraft_version": mc_version,
        "mod_id": mod_id,
        "mod_group": safe_author,
        "mod_name": mod_name,
        "mod_authors": author,
        "package_name": package_name,
    })

    for tpl, output in [
        (templates_dir / "template.build.gradle.j2", mod_dir / "build.gradle"),
        (templates_dir / "template.gradle.properties.j2", mod_dir / "gradle.properties"),
        (templates_dir / "template.MainMod.java.j2", src_main_java_mod / "MainMod.java"),
        (templates_dir / "template.pack.mcmeta.j2", src_main_resources / "pack.mcmeta"),
    ]:
        render_template(tpl, context, output)

    cwd = Path(".").resolve()
    settings_path = cwd / "settings.gradle"
    is_workspace = settings_path.exists()

    if not is_workspace:
        gradle_dir = mod_dir / "gradle" / "wrapper"
        gradle_dir.mkdir(parents=True, exist_ok=True)
        for tpl_file, dst_file in [
            (".gitignore", mod_dir / ".gitignore"),
            (".gitattributes", mod_dir / ".gitattributes"),
            ("gradlew", mod_dir / "gradlew"),
            ("gradlew.bat", mod_dir / "gradlew.bat"),
            ("template.settings.gradle.j2", mod_dir / "settings.gradle"),
            ("gradle/wrapper/gradle-wrapper.jar", gradle_dir / "gradle-wrapper.jar"),
            ("gradle/wrapper/gradle-wrapper.properties", gradle_dir / "gradle-wrapper.properties"),
        ]:
            shutil.copy2(templates_dir / tpl_file, dst_file)

        download_evermod_module(mc_version, src_main_java)
    else:
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

    print(f"\n✅ Mod '{mod_name}' created successfully!")
    print(f"📦 Minecraft {mc_version} (Forge {version_info['forge_version']})")
    print(f"📂 Location: {mod_dir}")
    print(f"🏗️ Workspace mode: {'ON' if is_workspace else 'OFF'}")
    print("--------------------------------")

    refresh_environment()
