import subprocess
from pathlib import Path
import shutil

# ====================================================
# 📦 EverMod Publisher Utility
# Publishes signed releases to the 'releases' branch
# and updates 'latest/' only for stable versions.
# ====================================================

def run_command(cmd, cwd=None, silent=False):
    """Utility to run shell commands with optional live output."""
    if not silent:
        print(f"> {' '.join(cmd)}")
    result = subprocess.run(cmd, cwd=cwd, text=True, capture_output=silent)
    if result.returncode != 0:
        if not silent:
            print(f"❌ Command failed: {' '.join(cmd)}")
            if result.stderr:
                print(result.stderr)
        raise SystemExit(result.returncode)
    return result.stdout.strip()


def ensure_releases_branch():
    """Ensure the 'releases' branch exists remotely and locally."""
    current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], silent=True)
    print(f"🧭 Current branch: {current_branch}")

    run_command(["git", "fetch", "--all"], silent=True)
    branches = run_command(["git", "branch", "-a"], silent=True)

    if "remotes/origin/releases" not in branches:
        print("🌱 Creating remote branch 'releases' (empty)...")
        run_command(["git", "checkout", "--orphan", "releases"])
        run_command(["git", "reset", "--hard"])
        run_command(["git", "commit", "--allow-empty", "-m", "Initialize empty releases branch"])
        run_command(["git", "push", "origin", "releases"])
        run_command(["git", "checkout", current_branch])
    else:
        print("✅ Remote 'releases' branch found.")


def is_prerelease(tag: str) -> bool:
    """Return True if version tag contains prerelease indicators."""
    tag_lower = tag.lower()
    return any(word in tag_lower for word in ["beta", "alpha", "release_candidate", "rc"])


def publish_release(release_tag: str, source_dir: Path):
    """
    Publishes a release folder (e.g. releases/1.2.0)
    into the 'releases' branch and updates 'latest/' alias
    only if the version is stable.
    """
    ensure_releases_branch()

    prerelease = is_prerelease(release_tag)
    current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], silent=True)

    print(f"\n🚀 Publishing EverMod release {release_tag}...\n")

    run_command(["git", "checkout", "releases"])
    run_command(["git", "pull", "origin", "releases"])

    release_path = Path("releases") / release_tag
    latest_path = Path("releases") / "latest"

    if not source_dir.exists():
        print(f"❌ Source directory not found: {source_dir}")
        run_command(["git", "checkout", current_branch])
        return

    # --- Copy version folder ---
    if release_path.exists():
        shutil.rmtree(release_path)
    shutil.copytree(source_dir, release_path)

    # --- Optionally update 'latest/' alias ---
    if not prerelease:
        if latest_path.exists():
            shutil.rmtree(latest_path)
        shutil.copytree(source_dir, latest_path)
        print(f"🔁 Updated 'latest/' → {release_tag}")
    else:
        print(f"⚠️  Pre-release detected ({release_tag}), skipping update of 'latest/'")

    # --- Commit and push changes ---
    run_command(["git", "add", "releases/"])
    msg_suffix = "(pre-release)" if prerelease else "(stable)"
    run_command(["git", "commit", "-m", f"Release {release_tag} {msg_suffix}"])
    run_command(["git", "push", "origin", "releases"])

    # Return to main branch
    run_command(["git", "checkout", current_branch])

    print(f"\n✅ Release {release_tag} published successfully! {'(no latest update)' if prerelease else '(latest updated)'}\n")

def create_main_tag(release_tag: str, auto: bool = False):
    """
    Creates a Git tag for the given release.
    - If --auto is enabled, always tags on 'main' without asking.
    - Otherwise, asks user if not on 'main'.
    Automatically switches to the target branch and returns back.
    """
    print(f"\n 🏷️  Creating tag for release {release_tag}...\n")

    current_branch = run_command(["git", "rev-parse", "--abbrev-ref", "HEAD"], silent=True)
    tag_name = release_tag if release_tag.startswith("v") else f"v{release_tag}"

    # Check if tag already exists
    existing_tags = run_command(["git", "tag"], silent=True).splitlines()
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
        run_command(["git", "checkout", target_branch])
        run_command(["git", "pull", "origin", target_branch], silent=True)
    else:
        print(f"📍 Tag will be created on branch '{target_branch}'.")

    # Try to sign tag if GPG is configured
    try:
        run_command(["git", "tag", "-s", tag_name, "-m", f"EverMod {release_tag} release"])
        print(f"✅ Created signed tag: {tag_name}")
    except SystemExit:
        print("⚠️  GPG signing failed or not configured. Creating unsigned tag instead.")
        run_command(["git", "tag", "-a", tag_name, "-m", f"EverMod {release_tag} release"])
        print(f"✅ Created unsigned tag: {tag_name}")

    # Push tag
    run_command(["git", "push", "origin", tag_name])
    print(f"🚀 Tag {tag_name} pushed to remote repository on branch '{target_branch}'.")

    # Return to previous branch if changed
    if target_branch != current_branch:
        run_command(["git", "checkout", current_branch])
        print(f"↩️  Returned to previous branch: {current_branch}")

    print(f"✨ Tagging process for {tag_name} completed successfully.\n")

