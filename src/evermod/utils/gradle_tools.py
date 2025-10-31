import subprocess
import platform
from pathlib import Path

def refresh_environment():
    print("🔄 Refreshing Gradle and Java environment...")

    gradlew = Path("./gradlew")
    if not gradlew.exists():
        print("⚠️  gradlew not found in this directory.")
        return

    # Detect OS and use correct syntax
    if platform.system() == "Windows":
        gradle_cmd = [".\\gradlew.bat", "--refresh-dependencies"]
    else:
        gradle_cmd = ["./gradlew", "--refresh-dependencies"]

    try:
        subprocess.run(gradle_cmd, check=True, shell=True)
        print("✅ Gradle dependencies refreshed successfully.")
    except subprocess.CalledProcessError:
        print("❌ Failed to refresh Gradle dependencies.")

    print("\n💡 Tip: If you're using VS Code, run this after reload:")
    print("   → Press Ctrl + Shift + P → 'Java: Clean the Java language server workspace'")
    print("   (This ensures Forge and autocompletion are fully reindexed.)")
