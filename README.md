# ⚙️ EverMod CLI

**EverMod CLI** is the official command-line tool for the [EverMod Framework](https://github.com/wipodev/EverMod).  
It provides a unified way to **create, organize, and maintain modular Minecraft Forge mods** across multiple projects and versions.

With a single command, you can generate new mods from pre-configured MDK templates, manage Git submodules, and keep your workspace templates up to date — all without touching Gradle or Forge manually.

---

## 🚀 Key Features

- 🧱 **Create ready-to-build Forge mods** from official EverMod MDK templates.
- 📘 **Collect source code for AI-based documentation** using the `evermix` command.
- 🔗 **Add external mods as Git submodules** directly from GitHub.
- 🔄 **Update templates automatically**, with version comparison and `--force` reinstall.
- ⚙️ Fully **standalone executable** (`evermod.exe` / `evermod`), no Python required.
- 🪶 Works on **Windows**, **Linux**, and **macOS** (build script included).

---

## 🧰 Installation

You can install EverMod CLI in two ways:

### 🔹 Option 1 — Prebuilt Installers (Recommended)

Download the installer for your system from the **[Releases](https://github.com/wipodev/evermod-cli/releases)** section:

| Platform   | Installer           |
| ---------- | ------------------- |
| 🪟 Windows | `EverMod-Setup.exe` |
| 🐧 Linux   | `EverMod-Setup.run` |
| 🍎 macOS   | _(coming soon)_     |

The installer automatically:

- Copies the CLI to your system.
- Registers it in the `PATH` for global use.
- Initializes templates in your user directory (`~/.evermod`).

---

### 🔹 Option 2 — Build from source

If you prefer to modify or rebuild EverMod CLI yourself, clone the repository and run the build script:

```bash
git clone https://github.com/wipodev/evermod-cli.git
cd evermod-cli
python build.py
```

This script uses **PyInstaller** to generate platform-specific executables in the `dist/` folder.

---

## 🧭 Basic Usage

```bash
evermod [command] [options]
```

---

### 🧱 Create a new mod

```bash
evermod create MyMod 1.20.1
```

Creates a new mod in `mods/MyMod` using the Forge MDK template for the specified Minecraft version.  
If no version is specified, it defaults to **1.19.2**.

---

### 📘 Collect project source for AI documentation

```bash
evermod evermix
```

Collects source code from all mods in the workspace for AI-assisted documentation or analysis.  
You can also run it for a single mod:

```bash
evermod evermix SilentMask
```

---

### 🔗 Add an external mod as a Git submodule

```bash
evermod add wipodev John666
```

Clones `https://github.com/wipodev/John666.git` into `mods/John666`  
and registers it as a Git submodule automatically.

---

### 🔄 Update templates

```bash
evermod update
```

Checks for new EverMod MDK template versions and updates if available.  
Use `--force` to reinstall templates even if already up to date:

```bash
evermod update --force
```

---

### 📦 Show version info

```bash
evermod --version
```

Displays the current version of the EverMod CLI, the framework, and installed templates.

---

## 📁 Project Structure

```
evermod-cli/
├─ src/
│  └─ evermod/
│     ├─ main.py
│     ├─ commands/
│     │  ├─ create.py
│     │  ├─ evermix.py
│     │  ├─ add.py
│     │  ├─ update.py
│     │  └─ version.py
│     └─ utils/
│        └─ paths.py
├─ assets/
│  └─ icon.ico
├─ build.py
├─ manifest.json
└─ setup.iss
```

---

## ⚙️ Build manually (alternative)

If you want to build the executable manually without `build.py`:

```bash
pip install pyinstaller
pyinstaller --onefile src/evermod/main.py -n evermod --icon assets/icon.ico
```

This creates `dist/evermod.exe` (on Windows) or `dist/evermod` (on Linux/macOS).

---

## 🧠 Requirements (for building only)

- Python **3.10+**
- Git **2.30+**
- Inno Setup **6+**

---

## 🪄 Example workflow

```bash
# Create a new mod
evermod create SilentMask

# Collect all code for AI documentation
evermod evermix

# Add an external mod
evermod add myuser ExampleMod

# Force-update templates
evermod update --force
```

---

## 👨‍💻 Author

**WipoDev**  
🌐 [https://www.wipodev.com](https://www.wipodev.com)  
📦 [GitHub](https://github.com/wipodev)
🔨 [CurseForge](https://www.curseforge.com/members/wipodev/projects)

---

## 🪪 License

This project is licensed under the **Apache License 2.0**.  
You are free to use, modify, and distribute it, as long as proper attribution is provided.
