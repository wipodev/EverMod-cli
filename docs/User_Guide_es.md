# ⚙️ EverMod CLI — Guía de Usuario

**Autor:** WipoDev
**Versión:** 1.0
**Última actualización:** 2025-11-03

---

## 🌍 ¿Qué es EverMod CLI?

**EverMod CLI** es una herramienta de línea de comandos que permite crear, organizar y mantener proyectos de mods de Minecraft Forge utilizando el **EverMod Framework**.
Su objetivo es simplificar el flujo de trabajo, automatizando tareas como la creación de nuevos mods, la integración de submódulos y la actualización de plantillas.

---

## 🧰 Instalación

Descarga el instalador correspondiente a tu sistema operativo desde la sección **[Releases](https://github.com/wipodev/evermod-cli/releases)** del repositorio oficial.

| Plataforma | Instalador          |
| ---------- | ------------------- |
| 🪟 Windows | `EverMod-Setup.exe` |
| 🐧 Linux   | `EverMod-Setup.run` |
| 🍎 macOS   | _(próximamente)_    |

Una vez completada la instalación, abre una terminal y ejecuta el siguiente comando para descargar las plantillas necesarias:

```bash
evermod update
```

Este comando inicializa el entorno de plantillas EverMod en tu carpeta global (`~/.evermod/templates`), dejándolo listo para usar.

---

## 🚀 Uso básico

La sintaxis general es:

```bash
evermod [comando] [opciones]
```

Puedes ejecutar `evermod --help` para ver los comandos disponibles.

---

### 🧱 Crear un nuevo mod

```bash
evermod create MiNuevoMod 1.20.1
```

Crea un nuevo mod Forge completamente configurado para la versión de Minecraft especificada. Si no se indica una versión, se usará la más reciente disponible.

Durante el proceso, el asistente solicitará:

- Nombre del mod
- ID del mod (`modid`)
- Autor
- Paquete Java (`net.autor.modid`)

**Ejemplo de salida:**

```
✅ Mod 'MiNuevoMod' creado con éxito!
📦 Minecraft 1.20.1 (Forge 47.2.0)
📂 Ubicación: ./MiNuevoMod
🏗️ Modo workspace: OFF (proyecto independiente)
```

---

### 🔗 Agregar un mod externo como submódulo

```bash
evermod add wipodev John666
```

Clona `https://github.com/wipodev/John666.git` dentro de la carpeta `mods/John666` y lo registra como submódulo del workspace.
El CLI detecta automáticamente si estás trabajando dentro de un entorno multiproyecto y actualiza el archivo `settings.gradle`.

---

### 📘 Generar documentación con EverMix

```bash
evermod evermix
```

Genera un archivo XML con todos los archivos fuente del mod, listo para ser usado en herramientas de documentación o análisis asistido por IA.

También puedes aplicarlo sobre un mod específico:

```bash
evermod evermix SilentMask
```

El resultado se guarda como `SilentMask-evermix.xml`.

---

### 🔄 Actualizar plantillas de Forge

```bash
evermod update
```

Comprueba si existen nuevas versiones de las plantillas EverMod y las actualiza automáticamente.
Si deseas forzar una reinstalación completa:

```bash
evermod update --force
```

---

### 🧾 Ver información de versiones

```bash
evermod --version
```

Muestra la versión actual del CLI, la del framework y la de las plantillas instaladas.

**Ejemplo:**

```
🧩 Información de EverMod CLI
----------------------------
Versión CLI:           v1.0.0
Framework compatible:  v1.0.0
Plantillas instaladas: v1.2.1
```

---

### 🔁 Refrescar dependencias de Gradle

```bash
evermod refresh
```

Refresca las dependencias de Gradle del proyecto actual y limpia el entorno Java en el editor para evitar errores de indexación.

---

## 📂 Estructura de proyecto

### 🔹 Workspace (multiproyecto)

Cuando trabajas en modo workspace, la estructura típica es:

```
MiWorkspace/
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

El nombre del workspace será el que indiques al crearlo.

---

### 🔹 Proyecto independiente

Si eliges crear un proyecto fuera de un workspace, se generará una estructura igual a la de un mod estándar de Forge, pero con el código del framework **EverMod** incluido directamente en `src`:

```
MiMod/
├─ src/
│  ├─ main/java/net/
│  │          ├─ wipodev/mimod/
│  │          │       └─ MainMod.java
│  │          └─ evermod/
│  └─ main/resources/META-INF/mods.toml
├─ build.gradle
├─ gradle.properties
├─ gradlew
└─ settings.gradle
```

---

## 💡 Consejos de uso

- Después de instalar EverMod CLI, ejecuta `evermod update` para descargar las plantillas antes de crear tu primer mod.
- Usa `evermod create` dentro de la raíz del workspace para registrar automáticamente nuevos mods.
- Ejecuta `evermix` para generar documentación del proyecto y compartirla con herramientas de IA.
- Si usas VS Code, tras crear un mod ejecuta **Ctrl + Shift + P → “Java: Clean the Java language server workspace”** para reindexar.

---

## 🧱 Comandos disponibles

| Comando     | Descripción                                               |
| ----------- | --------------------------------------------------------- |
| `create`    | Crea un nuevo mod a partir de una plantilla MDK.          |
| `add`       | Agrega un mod existente como submódulo de Git.            |
| `evermix`   | Genera un paquete XML con el código fuente del proyecto.  |
| `update`    | Descarga y actualiza las plantillas oficiales de EverMod. |
| `refresh`   | Refresca dependencias y configuración Gradle.             |
| `--version` | Muestra información del CLI, framework y plantillas.      |

---

## 🪪 Licencia y autoría

Desarrollado por **WipoDev**
📦 [GitHub](https://github.com/wipodev)
🌐 [https://www.wipodev.com](https://www.wipodev.com)

Licenciado bajo **Apache License 2.0**.
Eres libre de usar y modificar EverMod CLI con la atribución correspondiente.
