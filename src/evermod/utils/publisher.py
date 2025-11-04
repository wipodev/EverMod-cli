import subprocess
from pathlib import Path
import shutil, tempfile

# ====================================================
# 📦 EverMod Publisher Utility
# Publishes signed releases to the 'releases' branch
# and updates 'latest/' only for stable versions.
# ====================================================

def run_command(cmd, cwd=None, silent=False):
    """Utility to run shell commands with optional live output."""
    if not silent:
        print(f"> {' '.join(cmd)}")
    if silent:
        result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=True)
        output = result.stdout.strip() if result.stdout else ""
    else:
        result = subprocess.run(cmd, cwd=cwd, text=True)
        output = ""
    if result.returncode != 0:
        print(f"❌ Command failed: {' '.join(cmd)}")
        if result.stderr:
            print(result.stderr)
        raise SystemExit(result.returncode)
    return output

def ensure_releases_branch(repo_path: Path | None = None):
    """Ensure the 'releases' branch exists remotely and locally."""
    cwd = repo_path or Path(".")
    current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, silent=True)
    print(f"🧭 Current branch: {current_branch}")

    run_command(["git", "fetch", "--all"], cwd=cwd, silent=True)
    branches = run_command(["git", "branch", "-a"], cwd=cwd, silent=True)

    if "remotes/origin/releases" not in branches:
        print("🌱 Creating remote branch 'releases' (empty)...")
        run_command(["git", "checkout", "--orphan", "releases"], cwd=cwd)
        run_command(["git", "reset", "--hard"], cwd=cwd)
        run_command(["git", "commit", "--allow-empty", "-m", "Initialize empty releases branch"], cwd=cwd)
        run_command(["git", "push", "origin", "releases"], cwd=cwd)
        run_command(["git", "checkout", current_branch], cwd=cwd)
    else:
        print("✅ Remote 'releases' branch found.")


def is_prerelease(tag: str) -> bool:
    """Return True if version tag contains prerelease indicators."""
    tag_lower = tag.lower()
    return any(word in tag_lower for word in ["beta", "alpha", "release_candidate", "rc"])


def publish_release(release_tag: str, source_dir: Path, repo_path: Path | None = None):
    """
    Publishes a release folder (e.g. releases/1.2.0)
    into the 'releases' branch and updates 'latest/' alias
    only if the version is stable.
    """
    cwd = repo_path or Path(".")
    
    # ✅ Move release folder to a temp safe path before git checkout
    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        return

    temp_dir = Path(tempfile.gettempdir()) / f"evermod_release_{release_tag}"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    shutil.copytree(source_dir, temp_dir)

    ensure_releases_branch(cwd)

    prerelease = is_prerelease(release_tag)
    current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, silent=True)

    print(f"\n🚀 Publishing EverMod release {release_tag}...\n")

    run_command(["git", "checkout", "releases"], cwd=cwd)
    run_command(["git", "pull", "origin", "releases"], cwd=cwd)

    release_path = cwd / "releases" / release_tag
    latest_path = cwd / "releases" / "latest"

    # --- Copy version folder (from temp instead of original) ---
    if release_path.exists():
        shutil.rmtree(release_path)
    shutil.copytree(temp_dir, release_path)

    # --- Optionally update 'latest/' alias ---
    if not prerelease:
        if latest_path.exists():
            shutil.rmtree(latest_path)
        shutil.copytree(temp_dir, latest_path)
        print(f"🔁 Updated 'latest/' → {release_tag}")
    else:
        print(f"⚠️  Pre-release detected ({release_tag}), skipping update of 'latest/'")

    # --- Commit and push changes ---
    run_command(["git", "add", "releases/"], cwd=cwd)
    msg_suffix = "(pre-release)" if prerelease else "(stable)"
    run_command(["git", "commit", "-m", f"Release {release_tag} {msg_suffix}"], cwd=cwd)
    run_command(["git", "push", "origin", "releases"], cwd=cwd)

    # Return to main branch
    run_command(["git", "checkout", current_branch], cwd=cwd)

    print(f"\n✅ Release {release_tag} published successfully! {'(no latest update)' if prerelease else '(latest updated)'}\n")

    # ✅ Cleanup
    shutil.rmtree(temp_dir, ignore_errors=True)


def create_main_tag(release_tag: str, auto: bool = False, repo_path: Path | None = None):
    """
    Creates a Git tag for the given release.
    - If --auto is enabled, always tags on 'main' without asking.
    - Otherwise, asks user if not on 'main'.
    Automatically switches to the target branch and returns back.
    """
    cwd = repo_path or Path(".")
    print(f"\n 🏷️  Creating tag for release {release_tag}...\n")

    current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=cwd, silent=True)
    tag_name = release_tag if release_tag.startswith("v") else f"v{release_tag}"

    # Check if tag already exists
    existing_tags = run_command(["git", "tag"], cwd=cwd, silent=True).splitlines()
    if tag_name in existing_tags:
        print(f" ℹ️  Tag {tag_name} already exists, skipping creation.")
        return

    # Determine target branch
    target_branch = "main" if auto else current_branch

    if not auto and current_branch != "main":
        print(f"⚠️  You are currently on branch '{current_branch}', not 'main'.")
        choice = input("Do you want to create the tag on 'main' instead? (y/n): ").strip().lower()
        if choice == "y":
            target_branch = "main"

    # Switch branch if necessary
    if target_branch != current_branch:
        print(f"🔀 Switching from '{current_branch}' → '{target_branch}' to create the tag...")
        run_command(["git", "checkout", target_branch], cwd=cwd)
        run_command(["git", "pull", "origin", target_branch], cwd=cwd, silent=True)
    else:
        print(f"📍 Tag will be created on branch '{target_branch}'.")

    # Try to sign tag if GPG is configured
    try:
        run_command(["git", "tag", "-s", tag_name, "-m", f"EverMod {release_tag} release"], cwd=cwd)
        print(f"✅ Created signed tag: {tag_name}")
    except SystemExit:
        print("⚠️  GPG signing failed or not configured. Creating unsigned tag instead.")
        run_command(["git", "tag", "-a", tag_name, "-m", f"EverMod {release_tag} release"], cwd=cwd)
        print(f"✅ Created unsigned tag: {tag_name}")

    # Push tag
    run_command(["git", "push", "origin", tag_name], cwd=cwd)
    print(f"🚀 Tag {tag_name} pushed to remote repository on branch '{target_branch}'.")

    # Return to previous branch if changed
    if target_branch != current_branch:
        run_command(["git", "checkout", current_branch], cwd=cwd)
        print(f"↩️  Returned to previous branch: {current_branch}")

    print(f"✨ Tagging process for {tag_name} completed successfully.\n")
