# 🧩 EverMod CLI — Release Command (Technical Documentation)

## Overview

The `evermod release` command is the internal packaging and publishing system of the **EverMod Framework**.
It builds all versioned EverMod modules, generates a full workspace package, signs all metadata, and optionally publishes the release to the **`releases`** branch on GitHub.

> ⚠️ This command is for **internal use only** and is hidden from the public CLI help.
> It requires authorization through EverMod’s internal RSA key system.

---

## 🔧 Command Syntax

```bash
evermod release <version_tag> [--publish] [--auto] [target]
```

### Parameters

| Argument        | Description                                                                                                                        |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------- |
| `<version_tag>` | The release tag, e.g., `1.4.0`, `1.4.0-beta`, `1.5.0-rc1`.                                                                         |
| `--publish`     | Publishes the built release to the remote `releases` branch.                                                                       |
| `--auto`        | Skips prompts and automatically tags `main` after publishing.                                                                      |
| `[target]`      | Optional. Defines a custom target directory from which the release will be built (default is `.` — the current working directory). |

---

## 🧱 Build Structure

When executed, the command performs the following operations:

1. **Authorization Check**
   Uses the RSA-based function `require_internal_auth()` to verify that the local environment is authorized to build official releases.

2. **Clean Build Directory**
   Removes any previous folder under `releases/<version_tag>` before starting a new build.

3. **Module Compression**
   For each version module under `framework/evermod-*`, only the following path is included:

   ```
   src/main/java/net/
   ```

   Each one is compressed into a versioned ZIP:

   ```
   evermod-<mc_version>.zip
   ```

   Example: `evermod-1.19.2.zip` and `evermod-1.20.1.zip`.

   These ZIP files contain only the `net` package, keeping them lightweight and version-agnostic.

4. **Full Workspace Package**
   A complete ZIP archive named `evermod-framework.zip` is generated, containing the following structure:

   ```
   .vscode/
   framework/
   gradle/
   mods/
   .gitattributes
   .gitignore
   build.gradle
   gradle.properties
   gradlew
   gradlew.bat
   settings.gradle
   LICENSE
   README.md
   ```

   > All `build/` directories inside the `framework/` folder are automatically **excluded** to keep the archive clean.

5. **Metadata Generation (`versions.json`)**
   Creates a JSON file inside `releases/<version_tag>/` describing all artifacts:

   ```json
   {
     "schema": 1,
     "version": "1.4.0",
     "status": "stable",
     "date": "2025-11-03",
     "modules": {
       "1.19.2": {
         "path": "releases/1.4.0/evermod-1.19.2.zip",
         "size": "403KB",
         "sha256": "d5d15d0d..."
       },
       "1.20.1": {
         "path": "releases/1.4.0/evermod-1.20.1.zip",
         "size": "417KB",
         "sha256": "9b7f84ac..."
       }
     },
     "workspace": {
       "path": "releases/1.4.0/evermod-framework.zip",
       "size": "3.2MB",
       "sha256": "4a6d9ccf..."
     }
   }
   ```

---

## 🔏 Digital Signing

After generating `versions.json`, the file is cryptographically signed using the developer’s private RSA key via `sign_file()` from `evermod.auth.security`.

The generated signature file is stored as:

```
versions.json.sig
```

This ensures the authenticity and integrity of every release artifact.

---

## 🚀 Publishing Flow

If the `--publish` flag is included, the command will:

1. **Push the Release to the `releases` Branch**

   - Calls `publish_release()` from `evermod.utils.publisher`.
   - Uploads all generated files to the remote branch.
   - Updates the `latest/` folder only for stable builds.

2. **Tag the Source Branch**

   - Executes `create_main_tag()` to create a version tag.
   - If `--auto` is used, it tags `main` directly.
   - If not, the CLI prompts:

     ```
     You are currently on branch 'dev', not 'main'.
     Do you want to create the tag on 'main' instead? (y/n)
     ```

3. **Tag Formatting**
   Tags are automatically prefixed with `v` if not included (e.g., `1.4.0` → `v1.4.0`).
   GPG signing is attempted if configured locally.

4. **Cleanup**
   Local temporary folders under `releases/` are removed, keeping the environment clean.

---

## 🧩 Repository Layout

### Main Branch (Development)

```
main/
├── framework/
├── src/
├── build.py
├── manifest.json
└── ...
```

### Releases Branch (Artifacts)

```
releases/
├── latest/
│   ├── evermod-1.20.1.zip
│   ├── evermod-framework.zip
│   ├── versions.json
│   └── versions.json.sig
├── 1.4.0/
│   ├── evermod-1.20.1.zip
│   ├── evermod-framework.zip
│   ├── versions.json
│   └── versions.json.sig
└── ...
```

Each release can be accessed publicly, for example:

```
https://wipodev.github.io/EverMod/releases/latest/versions.json
```

---

## ⚙️ Internal Helper Functions

| Function                  | Module                    | Purpose                                                    |
| ------------------------- | ------------------------- | ---------------------------------------------------------- |
| `require_internal_auth()` | `evermod.auth.security`   | Validates internal authorization.                          |
| `sign_file()`             | `evermod.auth.security`   | Signs a file with the developer's private RSA key.         |
| `publish_release()`       | `evermod.utils.publisher` | Pushes the release folder to the remote `releases` branch. |
| `is_prerelease()`         | `evermod.utils.publisher` | Detects prerelease versions like alpha/beta/rc.            |
| `create_main_tag()`       | `evermod.utils.publisher` | Creates and pushes a version tag to Git.                   |

---

## ✅ Best Practices

- Run the command only from the latest commit of `main` or `dev`.
- Never push the local `releases/` folder — it’s ignored by design.
- Keep your private key secure (`~/.evermod/keys/private.pem`).
- Use `--auto` in CI/CD pipelines for automated versioning.
- Use `[target]` when generating releases from a custom workspace path.
- Prerelease tags (`beta`, `alpha`, `rc`) do not overwrite the `latest/` alias.

---

## 🧩 Future Enhancements

Planned improvements:

- Multiple release channels (`stable`, `beta`, `snapshot`).
- Automatic diffing between framework versions.
- Integration with GitHub Actions.
- Incremental rebuild system for modules.
- Enhanced checksum verification pipeline.

---

## 📚 Author Notes

The EverMod release system ensures full reproducibility and verifiable integrity.
Every generated artifact can be validated through checksum and cryptographic signature.
This process enforces EverMod’s philosophy of **modular integrity** and **workspace reproducibility**, ensuring each framework version remains a fully self-contained environment ready for develop
