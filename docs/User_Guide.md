# ⚙️ EverMod CLI — User Guide

**Author:** WipoDev
**Version:** 1.0
**Last Updated:** 2025-11-03

---

## 🌍 What is EverMod CLI?

**EverMod CLI** is a command-line tool that allows you to create, organize, and maintain Minecraft Forge mod projects using the **EverMod Framework**.
Its goal is to simplify your workflow by automating repetitive tasks such as creating new mods, integrating Git submodules, and updating templates.

---

## 🧰 Installation

Download the installer for your operating system from the **[Releases](https://github.com/wipodev/evermod-cli/releases)** section of the official repository.

| Platform   | Installer           |
| ---------- | ------------------- |
| 🪟 Windows | `EverMod-Setup.exe` |
| 🐧 Linux   | `EverMod-Setup.run` |
| 🍎 macOS   | _(coming soon)_     |

Once the installation is complete, open a terminal and run the following command to download the required templates:

```bash
evermod update
```

This command initializes the EverMod template environment in your global folder (`~/.evermod/templates`), making it ready for use.

---

## 🚀 Basic Usage

General syntax:

```bash
evermod [command] [options]
```

You can run `evermod --help` to display all available commands.

---

### 🧱 Create a New Mod

```bash
evermod create MyNewMod 1.20.1
```

Creates a fully configured Forge mod for the specified Minecraft version. If no version is provided, the latest available version is used by default.

During the process, the wizard will ask for:

- Mod name
- Mod ID (`modid`)
- Author
- Java package (`net.author.modid`)

**Example output:**

```
✅ Mod 'MyNewMod' created successfully!
📦 Minecraft 1.20.1 (Forge 47.2.0)
📂 Location: ./MyNewMod
🏗️ Workspace mode: OFF (independent project)
```

---

### 🔗 Add an External Mod as a Submodule

```bash
evermod add wipodev John666
```

Clones `https://github.com/wipodev/John666.git` into `mods/John666` and registers it as a Git submodule.
The CLI automatically detects if you’re working inside a multi-project workspace and updates the `settings.gradle` file accordingly.

---

### 📘 Generate Documentation with EverMix

```bash
evermod evermix
```

Generates a single XML file containing all source files of the project, ready for documentation or AI-assisted analysis.

You can also target a specific mod:

```bash
evermod evermix SilentMask
```

The result is saved as `SilentMask-evermix.xml`.

---

### 🔄 Update Forge Templates

```bash
evermod update
```

Checks for new versions of the official EverMod templates and updates them automatically.
To force a complete reinstallation:

```bash
evermod update --force
```

---

### 🧾 Show Version Information

```bash
evermod --version
```

Displays the current version of the CLI, the framework, and the installed templates.

**Example:**

```
🧩 EverMod CLI Information
----------------------------
CLI Version:           v1.0.0
Compatible Framework:  v1.0.0
Installed Templates:   v1.2.1
```

---

### 🔁 Refresh Gradle Dependencies

```bash
evermod refresh
```

Refreshes the project's Gradle dependencies and cleans the Java environment in your IDE to prevent indexing issues.

---

## 📂 Project Structure

### 🔹 Workspace (Multi-Project)

When working in workspace mode, the typical structure looks like this:

```
MyWorkspace/
├─ framework/
│  ├─ evermod-base/
│  ├─ evermod-1.19.2/
│  └─ evermod-1.20.1/
├─ mods/
│  ├─ John666/
│  └─ SilentMask/
├─ gradle/
├─ build.gradle
├─ settings.gradle
├─ gradlew
└─ README.md
```

The workspace name will match the one you specified during creation.

---

### 🔹 Independent Project

If you create a mod outside a workspace, it will follow the standard Forge structure, but with the **EverMod** framework integrated directly inside the `src` folder:

```
MyMod/
├─ src/
│  ├─ main/java/net/
│  │          ├─ wipodev/mymod/
│  │          │       └─ MainMod.java
│  │          └─ evermod/
│  └─ main/resources/META-INF/mods.toml
├─ build.gradle
├─ gradle.properties
├─ gradlew
└─ settings.gradle
```

---

## 💡 Usage Tips

- After installing EverMod CLI, run `evermod update` before creating your first mod to ensure the templates are ready.
- Use `evermod create` inside the workspace root to automatically register new mods.
- Run `evermix` to generate documentation packages that can be analyzed by AI tools.
- In VS Code, after creating a mod, press **Ctrl + Shift + P → “Java: Clean the Java language server workspace”** to reindex your environment.

---

## 🧱 Available Commands

| Command     | Description                                                    |
| ----------- | -------------------------------------------------------------- |
| `create`    | Creates a new mod from an MDK template.                        |
| `add`       | Adds an existing mod as a Git submodule.                       |
| `evermix`   | Generates an XML package containing the project's source code. |
| `update`    | Downloads and updates the official EverMod templates.          |
| `refresh`   | Refreshes Gradle dependencies and configuration.               |
| `--version` | Displays CLI, framework, and template version information.     |

---

## 🪪 License & Author

Developed by **WipoDev**
📦 [GitHub](https://github.com/wipodev)
🌐 [https://www.wipodev.com](https://www.wipodev.com)

Licensed under the **Apache License 2.0**.
You are free to use and modify EverMod CLI with proper attribution.
