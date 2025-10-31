import subprocess
from pathlib import Path
from evermod.utils.gradle_tools import refresh_environment

def run(user: str, name: str, target_path: str = "."):
    cwd = Path(".").resolve()  # workspace root
    target_base = Path(target_path).resolve()  # where to add the submodule
    repo_url = f"https://github.com/{user}/{name}.git"
    dest = target_base / name

    print(f"📦 Adding submodule '{name}' from {repo_url}...")

    if dest.exists():
        print(f"⚠️  A folder named '{name}' already exists in {target_base}")
        return

    try:
        relative_dest = str(dest.relative_to(cwd))
        subprocess.run(["git", "submodule", "add", repo_url, relative_dest], check=True)
        print(f"✅ Submodule '{name}' added successfully.")
    except subprocess.CalledProcessError:
        print(f"❌ Failed to add submodule '{name}'.")
        return

    # Detect workspace in the directory where the command was executed
    settings_path = cwd / "settings.gradle"
    if settings_path.exists():
        relative_path = dest.relative_to(cwd)
        include_path = str(relative_path).replace("\\", ":").replace("/", ":")
        include_line = f'include("{include_path}")'
        
        content = settings_path.read_text(encoding="utf-8")
        if include_line not in content:
            with open(settings_path, "a", encoding="utf-8") as f:
                f.write(f"\n{include_line}\n")
            print(f"🧩 Submodule '{name}' registered in workspace settings.gradle")
        else:
            print(f"ℹ️  Submodule '{name}' already registered in workspace.")

    print(f"🏗️ Workspace mode: {'ON' if settings_path.exists() else 'OFF'}")
    refresh_environment()
