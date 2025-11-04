import shutil
from pathlib import Path
from evermod.utils.paths import get_templates_dir

def create_mod_structure(mod_dir: Path, package_parts: list[str]):
    """Create folder structure and copy static template files."""
    src_main_java = mod_dir / "src" / "main" / "java"
    src_main_java_mod = src_main_java / Path(*package_parts)
    src_main_resources = mod_dir / "src" / "main" / "resources"
    src_main_metainf = src_main_resources / "META-INF"

    src_main_java_mod.mkdir(parents=True, exist_ok=True)
    src_main_resources.mkdir(parents=True, exist_ok=True)
    src_main_metainf.mkdir(parents=True, exist_ok=True)

    templates_dir = get_templates_dir()

    for tpl_file, dst_file in [
        ("mods.toml", src_main_resources / "mods.toml"),
        ("pack.mcmeta", src_main_metainf / "pack.mcmeta"),
        ("LICENSE.txt", mod_dir / "LICENSE.txt"),
    ]:
        shutil.copy2(templates_dir / tpl_file, dst_file)

    return templates_dir, src_main_java, src_main_java_mod
