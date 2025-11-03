# 🧩 EverMod CLI — Comando Release (Documentación Técnica)

## Descripción general

El comando `evermod release` es el sistema interno de empaquetado y publicación del **EverMod Framework**.
Se encarga de compilar todos los módulos versionados de EverMod, generar un paquete completo del espacio de trabajo, firmar los metadatos y, opcionalmente, publicar la versión en la rama **`releases`** de GitHub.

> ⚠️ Este comando es de **uso interno** y está oculto del menú de ayuda público del CLI.
> Requiere autorización mediante el sistema interno de claves RSA de EverMod.

---

## 🔧 Sintaxis del comando

```bash
evermod release <version_tag> [--publish] [--auto] [target]
```

### Parámetros

| Argumento       | Descripción                                                                                                                              |
| --------------- | ---------------------------------------------------------------------------------------------------------------------------------------- |
| `<version_tag>` | Etiqueta de la versión, por ejemplo: `1.4.0`, `1.4.0-beta`, `1.5.0-rc1`.                                                                 |
| `--publish`     | Publica la versión generada en la rama remota `releases`.                                                                                |
| `--auto`        | Omite confirmaciones y etiqueta automáticamente la rama `main` después de publicar.                                                      |
| `[target]`      | Opcional. Define un directorio de destino personalizado desde el cual se construirá la versión (por defecto `.` — el directorio actual). |

---

## 🧱 Estructura del proceso de construcción

Cuando se ejecuta, el comando realiza las siguientes operaciones:

1. **Verificación de autorización**
   Utiliza la función basada en RSA `require_internal_auth()` para verificar que el entorno local esté autorizado a generar versiones oficiales.

2. **Limpieza del directorio de compilación**
   Elimina cualquier carpeta previa bajo `releases/<version_tag>` antes de iniciar la nueva compilación.

3. **Compresión de módulos**
   Para cada módulo dentro de `framework/evermod-*`, solo se incluye la siguiente ruta:

   ```
   src/main/java/net/
   ```

   Cada uno se comprime en un archivo ZIP versionado:

   ```
   evermod-<mc_version>.zip
   ```

   Ejemplo: `evermod-1.19.2.zip` y `evermod-1.20.1.zip`.

   Estos ZIP contienen únicamente el paquete `net`, manteniéndolos ligeros y separados por versión.

4. **Paquete completo del workspace**
   Se genera un archivo ZIP completo llamado `evermod-framework.zip`, que contiene la siguiente estructura:

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

   > Todas las carpetas `build/` dentro de `framework/` se **excluyen automáticamente** para mantener el paquete limpio.

5. **Generación del archivo de metadatos (`versions.json`)**
   Crea un archivo JSON dentro de `releases/<version_tag>/` que describe todos los artefactos generados:

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

## 🔏 Firma digital

Después de generar `versions.json`, el archivo se firma criptográficamente con la clave privada RSA del desarrollador mediante la función `sign_file()` del módulo `evermod.auth.security`.

El archivo de firma generado se guarda como:

```
versions.json.sig
```

Esto garantiza la autenticidad e integridad de cada artefacto publicado.

---

## 🚀 Flujo de publicación

Si se incluye la opción `--publish`, el comando ejecuta los siguientes pasos:

1. **Publicar la versión en la rama `releases`**

   - Llama a `publish_release()` desde `evermod.utils.publisher`.
   - Sube todos los archivos generados a la rama remota.
   - Actualiza la carpeta `latest/` únicamente para versiones estables.

2. **Etiquetar la rama de origen**

   - Ejecuta `create_main_tag()` para crear una etiqueta (`tag`).
   - Si se usa `--auto`, etiqueta directamente la rama `main`.
   - Si no, el CLI pedirá confirmación:

     ```
     You are currently on branch 'dev', not 'main'.
     Do you want to create the tag on 'main' instead? (y/n)
     ```

3. **Formato de etiquetas**
   Las etiquetas se prefijan automáticamente con `v` si no se incluye (por ejemplo, `1.4.0` → `v1.4.0`).
   Si GPG está configurado, las etiquetas se firman automáticamente.

4. **Limpieza**
   Las carpetas temporales locales bajo `releases/` se eliminan al finalizar, dejando el entorno limpio.

---

## 🧩 Estructura del repositorio

### Rama principal (desarrollo)

```
main/
├── framework/
├── src/
├── build.py
├── manifest.json
└── ...
```

### Rama de publicaciones (artefactos)

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

Cada publicación puede accederse públicamente, por ejemplo:

```
https://wipodev.com/EverMod/releases/latest/versions.json
```

---

## ⚙️ Funciones internas auxiliares

| Función                   | Módulo                    | Propósito                                                          |
| ------------------------- | ------------------------- | ------------------------------------------------------------------ |
| `require_internal_auth()` | `evermod.auth.security`   | Verifica la autorización interna para generar versiones oficiales. |
| `sign_file()`             | `evermod.auth.security`   | Firma un archivo con la clave privada RSA del desarrollador.       |
| `publish_release()`       | `evermod.utils.publisher` | Publica la carpeta de la versión en la rama remota `releases`.     |
| `is_prerelease()`         | `evermod.utils.publisher` | Detecta si una versión es de tipo alpha/beta/rc.                   |
| `create_main_tag()`       | `evermod.utils.publisher` | Crea y sube una etiqueta de versión a Git.                         |

---

## ✅ Buenas prácticas

- Ejecutar el comando solo desde el último commit de `main` o `dev`.
- Nunca subir la carpeta local `releases/`; está ignorada por diseño.
- Mantener la clave privada segura (`~/.evermod/keys/private.pem`).
- Usar `--auto` en entornos CI/CD para versionado automático.
- Usar `[target]` al generar versiones desde un workspace personalizado.
- Las versiones `beta`, `alpha` o `rc` no actualizan el alias `latest/`.

---

## 🧩 Mejoras futuras

Mejoras planificadas:

- Múltiples canales de publicación (`stable`, `beta`, `snapshot`).
- Comparación automática entre versiones del framework.
- Integración con GitHub Actions.
- Sistema de reconstrucción incremental de módulos.
- Validación de integridad mediante sumas de verificación mejoradas.

---

## 📚 Notas del autor

El sistema de publicación de EverMod garantiza **reproducibilidad total** e **integridad verificable**.
Cada artefacto generado puede validarse mediante suma de verificación y firma criptográfica.
Este proceso refuerza la filosofía de **integridad modular** y **reproducibilidad del entorno de trabajo**, asegurando que cada versión del framework sea un entorno de desarrollo autocontenido listo para su distribución.
