# ⚙️ EverMod CLI

<p align="center">
<img src="./assets/icon.ico" alt="logo" width="50%">
</p>

**EverMod CLI** is the official command-line tool for the [EverMod Framework](https://github.com/wipodev/EverMod).
It provides a unified way to **create, organize, and maintain modular Minecraft Forge modding workspaces**.

With a single command, you can generate new mods, manage templates, or collect source code for documentation — all from a single, consistent interface.

---

## 🚀 Key Features

- 🧱 **Create ready-to-build Forge mods** using official EverMod templates.
- 🔗 **Add external mods** as Git submodules with automatic workspace registration.
- 📘 **Generate EverMix XML packages** for AI-assisted documentation and analysis.
- 🔄 **Update templates** easily through the `update` command.
- ⚙️ **Integrated release system** for internal packaging and version management.
- 🪶 Works on **Windows**, **Linux**, and **macOS**.

---

## 🧰 Installation

Download the installer for your platform from the **[Releases](https://github.com/wipodev/evermod-cli/releases)** section:

| Platform   | Installer           |
| ---------- | ------------------- |
| 🪟 Windows | `EverMod-Setup.exe` |
| 🐧 Linux   | `EverMod-Setup.run` |
| 🍎 macOS   | _(coming soon)_     |

After installation, open a terminal and run:

```bash
evermod update
```

This initializes your local EverMod template environment, preparing it for use.

---

## 🧭 Basic Commands

| Command                           | Description                                                 |
| --------------------------------- | ----------------------------------------------------------- |
| `evermod create <name> [version]` | Create a new mod project from a Forge MDK template.         |
| `evermod add <user> <repo>`       | Add a mod from GitHub as a submodule.                       |
| `evermod evermix [target]`        | Generate an EverMix XML package for documentation.          |
| `evermod update [--force]`        | Update or reinstall the EverMod templates.                  |
| `evermod refresh`                 | Refresh Gradle dependencies and Java indexes.               |
| `evermod --version`               | Show version information for CLI, framework, and templates. |

> 💡 The `release` command is reserved for internal framework builds and is hidden from the public CLI help.

---

## 📚 Documentation

Detailed documentation is available in the **[`docs/`](./docs/)** folder:

- [User Guide (docs/)](./docs/) — installation, usage, and workspace setup.
- [Technical Documentation](./docs/) — developer internals and release system.

---

## 🪄 Example Workflow

```bash
# Update templates (first-time setup)
evermod update

# Create a new mod project
evermod create SilentMask 1.20.1

# Add an existing mod from GitHub
evermod add wipodev John666

# Generate EverMix documentation
evermod evermix
```

---

## 👨‍💻 Author

**WipoDev**
🌐 [https://www.wipodev.com](https://www.wipodev.com)
📦 [GitHub](https://github.com/wipodev)

---

## 🪪 License

Licensed under the **Apache License 2.0**.
You are free to use, modify, and distribute EverMod CLI with proper attribution.
