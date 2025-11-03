# 🧠 EverMod CLI — Documentación Técnica

**Autor:** WipoDev
**Versión:** 1.0
**Última actualización:** 2025-11-03

---

## 📘 Descripción general

**EverMod CLI** es la herramienta de línea de comandos del [EverMod Framework](https://github.com/wipodev/EverMod).
Proporciona un entorno automatizado para **crear, mantener, documentar y publicar proyectos de modding Forge** dentro de un sistema de espacios de trabajo unificado.

Este documento está dirigido a **desarrolladores técnicos y mantenedores**, no a usuarios finales. Cubre la arquitectura interna, el flujo de comandos, el sistema de empaquetado y la automatización de compilación del CLI.

---

## 🧱 Estructura del proyecto

```
evermod-cli/
├── build.py                     # Automatización de compilado (PyInstaller + Inno Setup)
├── evermod.spec                 # Especificación de PyInstaller
├── src/evermod/
│   ├── main.py                  # Punto de entrada principal del CLI
│   ├── auth/                    # Sistema interno de claves RSA
│   ├── commands/                # Subcomandos del CLI
│   └── utils/                   # Utilidades auxiliares
├── docs/                        # Carpeta de documentación
├── manifest.json                # Metadatos del CLI
├── setup.iss                    # Instalador de Windows (Inno Setup)
└── requirements.txt             # Dependencias de Python
```

---

## ⚙️ Arquitectura principal

### 🧩 Punto de entrada (`main.py`)

- Usa `argparse` para definir la sintaxis de los comandos.
- Registra dinámicamente los subcomandos mediante `subparsers`.
- Oculta el comando interno `release` del menú de ayuda público.
- Dirige la ejecución a los manejadores correspondientes:

```python
match args.command:
    case "create": create.run()
    case "evermix": evermix.run(args.target)
    case "add": add.run(args.user, args.name, args.target)
    case "update": update.run(args.force, args.silent)
    case "refresh": gradle_tools.refresh_environment()
    case "release": release.run(args.release_tag, args.publish, args.auto, args.target)
```

El CLI funciona en **modo workspace** cuando se ejecuta dentro de un proyecto Gradle multiproyecto (detectando `settings.gradle`), o en **modo independiente** cuando se usa en un mod aislado.

---

## 🧩 Módulos de comandos

Cada comando se encuentra en `src/evermod/commands/` y expone un método `run()`.
Están diseñados para ser atómicos, independientes y reutilizables.

### 1. `create.py` — Asistente de creación de mods

- Asistente interactivo que construye un nuevo mod Forge a partir de las plantillas MDK de EverMod.
- Utiliza **Jinja2** para renderizar archivos `.java`, `.gradle` y `.properties`.
- Detecta automáticamente si está en un workspace.
- Registra el nuevo mod en `settings.gradle` si corresponde.
- Genera:

  - Directorios fuente (`src/main/java`, `resources`)
  - Gradle wrapper (si es independiente)
  - Archivos de metadatos predefinidos (`mods.toml`, `pack.mcmeta`, `LICENSE.txt`)

**Funciones clave:**

- `_sanitize_string()` → asegura nombres válidos para el modid.
- `_sanitize_package()` → formatea paquetes de Java válidos.
- `refresh_environment()` → fuerza la reindexación de Gradle tras la creación.

---

### 2. `add.py` — Agregar submódulo Git

- Automatiza `git submodule add https://github.com/<usuario>/<mod>.git`.
- Registra automáticamente el submódulo en `settings.gradle`.
- Refresca las dependencias de Gradle al finalizar.

**Flujo:**

1. Clona el repositorio en `/mods/<mod>`.
2. Agrega la línea `include("mods:<mod>")` a `settings.gradle`.
3. Llama a `gradle_tools.refresh_environment()`.

---

### 3. `evermix.py` — Sistema de consolidación de código fuente

- Recolecta el código de un proyecto y genera un XML único (`<project>`) para análisis o documentación asistida por IA.
- Excluye binarios y artefactos de compilación usando `.gitignore` + `evermix.config.json`.
- Incluye conteo de tokens y detección de archivos binarios.

**Ejemplo de salida:**

```xml
<?xml version="1.0" encoding="UTF-8"?>
<project>
  <context>Generado por EverMix para análisis y documentación.</context>
  <structure>
    <path>src/main/java/.../MainMod.java</path>
    <path type="binary">assets/icon.ico</path>
  </structure>
  <file name="MainMod.java"> ... </file>
</project>
```

---

### 4. `update.py` — Actualizador de plantillas

- Descarga la versión más reciente de las **plantillas EverMod** desde GitHub.
- Compara versiones usando la librería `packaging`.
- Clona las nuevas plantillas en `~/.evermod/templates`.
- Actualiza el manifiesto local `version.json`.
- Soporta banderas:

  - `--force` → reinstala incluso si ya está actualizada.
  - `--silent` → suprime interacción (usado por el instalador).

---

### 5. `version.py` — Información de versiones

- Muestra la versión de:

  - El CLI (`manifest.json`)
  - La versión compatible del framework
  - La versión instalada de las plantillas (desde la ruta global)

**Ejemplo:**

```
🧩 Información de EverMod CLI
----------------------------
Versión CLI:             v1.0.0
Framework compatible:    v1.0.0
Plantillas instaladas:   v1.2.1
Fecha de lanzamiento:    2025-11-03
Ruta global:             C:\Users\<usuario>\.evermod
```

---

### 6. `release.py` — Generador interno de versiones

> **Comando restringido.** Requiere autorización RSA interna válida.

Empaqueta el framework completo y publica nuevas versiones.
Ver `docs/EverMod_Release_System.md` para detalles completos.

**Resumen:**

1. Autenticación mediante `require_internal_auth()`.
2. Comprime los módulos `framework/evermod-*` en archivos ZIP.
3. Crea `evermod-framework.zip` (paquete completo de workspace).
4. Genera y firma `versions.json`.
5. Opcionalmente publica en GitHub (`publish_release()`).
6. Crea etiquetas de versión (`create_main_tag()`).

---

## 🔐 Sistema de seguridad y autorización

### Arquitectura RSA

| Componente        | Ruta                                       | Descripción                                          |
| ----------------- | ------------------------------------------ | ---------------------------------------------------- |
| **Clave pública** | `src/evermod/auth/keys/evermod_public.pem` | Distribuida dentro del ejecutable para verificación. |
| **Clave privada** | `~/.evermod/keys/private.pem`              | Clave local usada para firmar versiones internas.    |

El sistema firma y verifica mensajes y archivos usando **RSA + SHA256**.

**Ejemplo:**

```python
from evermod.auth.security import sign_file, verify_file_signature

sig_path = sign_file(Path('versions.json'))
verify_file_signature(Path('versions.json'), sig_path)
```

**Lógica de protección:**

- Comandos como `release` invocan `require_internal_auth()`.
- Si faltan claves o son inválidas, la ejecución se aborta.
- Cada `versions.json` se firma para garantizar su integridad.

---

## 🧰 Utilidades auxiliares

### `gradle_tools.py`

- Refresca las dependencias de Gradle en cualquier sistema operativo.
- Ejecuta `gradlew.bat` o `./gradlew` según corresponda.
- Muestra consejos para reindexar Java en VS Code.

### `paths.py`

- Abstracción de rutas globales:

  - `get_global_dir()` → `~/.evermod`
  - `get_templates_dir()` → `~/.evermod/templates`
  - `get_versions_file()` → `versions.json`
  - `get_manifest_path()` → Detecta el manifiesto tanto en modo fuente como compilado.

### `publisher.py`

- Publica versiones mediante Git:

  - Garantiza la existencia del branch `releases`.
  - Empuja los artefactos versionados.
  - Actualiza `latest/` solo para versiones estables.
  - Crea y firma etiquetas (GPG si está configurado).

---

## 🧩 Sistema de compilación (`build.py`)

Automatiza la creación de ejecutables y del instalador de Windows.

### 🧱 Pasos del build

1. **Sincronización de versiones** — Actualiza `setup.iss` y `pyproject.toml` con la versión del manifiesto.
2. **Limpieza** — Elimina carpetas de build previas.
3. **PyInstaller** — Genera `evermod.exe` usando `evermod.spec`.
4. **Inno Setup** — Crea el instalador `EverMod-Setup.exe`.
5. **Generación de claves (opcional)** — Produce el par RSA antes del build.

**Comando:**

```bash
python build.py --keys
```

Crea:

```
~/.evermod/keys/private.pem
src/evermod/auth/keys/evermod_public.pem
```

---

## 🧮 Dependencias

| Paquete          | Versión | Uso                                       |
| ---------------- | ------- | ----------------------------------------- |
| **Jinja2**       | 3.1.6   | Renderizado de plantillas MDK.            |
| **packaging**    | 25.0    | Comparación y parsing de versiones.       |
| **cryptography** | 46.0.3  | Firma RSA y verificación de archivos.     |
| **pathspec**     | 0.12.1  | Filtrado de rutas y exclusión en EverMix. |

Todas las dependencias se incluyen automáticamente dentro del ejecutable mediante PyInstaller.

---

## 🧭 Flujo de ejecución

```
Usuario → evermod create
      ↓
  main.py analiza argumentos
      ↓
  commands.create.run()
      ↓
  utils.paths / gradle_tools / plantillas Jinja2
```

---

## 🧩 Extensión del CLI

Para agregar un nuevo comando:

1. Crea un archivo en `src/evermod/commands/` (por ejemplo `deploy.py`).
2. Define una función `run()`.
3. Regístralo en `main.py` dentro de `subparsers`.
4. Reutiliza las utilidades existentes para mantener coherencia.

**Reglas básicas:**

- No sobrescribir archivos sin confirmación.
- Mantener compatibilidad multiplataforma.
- Incluir modos silencioso/interactivo según corresponda.

---

## ✅ Buenas prácticas

- Ejecutar builds desde un workspace limpio.
- Sincronizar `manifest.json` antes de empaquetar.
- No distribuir nunca las claves privadas.
- Actualizar plantillas periódicamente (`evermod update`).
- Usar `release --auto` solo en entornos CI/CD.

---

## 🪄 Mejoras futuras

- Integración con GitHub Actions (CI/CD).
- Archivo global de configuración.
- Soporte de plugins personalizados.
- Sistema de analítica opcional.
- Instaladores multiplataforma mejorados.

---

## ⚙️ Licencia

Licenciado bajo **Apache License 2.0**.
© 2025 WipoDev — Todos los derechos reservados.
