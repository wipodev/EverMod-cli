# 🧠 Informe Técnico — Sistema de Configuración de Reglas de Compilador (Java Lint Control)

**Proyecto:** EverMod CLI  
**Autor:** Wipodev  
**Estado:** Planeado (pendiente de implementación)  
**Fecha:** 2025-10-31  

---

## 🎯 Objetivo

Incorporar un sistema dentro de **EverMod CLI** que permita gestionar de forma centralizada el nivel de estrictitud del compilador Java y del análisis estático (JDT LS / VS Code) en los proyectos creados con EverMod.  

Este sistema busca ofrecer al desarrollador la posibilidad de alternar entre **modo estricto** (orientado a control de calidad y detección temprana de errores) y **modo relajado** (más práctico para desarrollo rápido y compatibilidad con Forge/Minecraft, donde los `@Nonnull` no siempre están bien definidos).

---

## ⚙️ Descripción funcional

### 1. Configuración base
El sistema se basará en un archivo de preferencias estándar:

```
.settings/org.eclipse.jdt.core.prefs
```

Este archivo define las políticas de advertencias y errores del compilador, incluyendo:

- Control de nulidad (`@Nonnull`, `@Nullable`)  
- Conversiones no comprobadas (`unchecked type conversion`)  
- Uso de tipos sin parametrizar (`raw type`)  
- Referencias no seguras (`nullReference`)  

Los valores admitidos son:  
`ignore`, `warning`, `error`.

---

### 2. Integración con EverMod CLI
El CLI incluirá un nuevo comando auxiliar:

```
evermod strict-mode <on|off>
```

Este comando modificará dinámicamente las reglas del archivo `.settings/org.eclipse.jdt.core.prefs` del proyecto o del workspace.

#### Ejemplo de uso:
```bash
evermod strict-mode on
```
→ Activa validaciones estrictas (`error` en referencias nulas, tipos sin control, etc.)

```bash
evermod strict-mode off
```
→ Desactiva validaciones innecesarias (`ignore` en null checks y genéricos)

---

### 3. Configuración por defecto
El CLI también podrá incluir plantillas predefinidas dentro de `templates/.settings/`:

- **strict.prefs** → configuración recomendada para entornos de desarrollo controlados.  
- **relaxed.prefs** → configuración ligera recomendada para mods de Forge.  

Durante la creación de un nuevo mod (`evermod create`), el CLI copiará automáticamente la configuración seleccionada.

---

## 🧩 Beneficios esperados

| Beneficio | Descripción |
|------------|-------------|
| **Consistencia** | Todos los mods EverMod compartirán las mismas reglas de análisis. |
| **Flexibilidad** | Permite alternar fácilmente entre entornos de desarrollo y revisión. |
| **Estandarización** | Evita conflictos de configuración entre IDEs (VS Code, Eclipse, IntelliJ). |
| **Control de calidad** | Facilita la detección temprana de errores reales sin ruido innecesario. |

---

## 🚀 Próximos pasos

1. Diseñar plantilla base `.settings/org.eclipse.jdt.core.prefs` con parámetros ajustables.  
2. Implementar comando `strict-mode` con reemplazo dinámico de líneas.  
3. Integrar copia automática de configuraciones en `evermod create`.  
4. Documentar en `README.md` y `helpStrictMode` la descripción de cada parámetro clave.