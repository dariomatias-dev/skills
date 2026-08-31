<br>
<div align="center">
<img src="https://img.shields.io/badge/Agent%20Skills-23-informational?style=for-the-badge" alt="Agent Skills">
<img src="https://img.shields.io/badge/Claude%20Code-compatible-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code">
<img src="https://img.shields.io/badge/Flutter-cubierto-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter">
<img src="https://img.shields.io/badge/Licencia-MIT-yellow?style=for-the-badge" alt="Licencia: MIT">
</div>
<br>

<p align="center">
<a href="README.md">English</a> · <strong>Español</strong> · <a href="README.pt-BR.md">Português (BR)</a>
</p>

<h1 align="center">Agent Skills</h1>

<p align="center">
<strong>Agent Skills</strong> de nivel de producción para Claude Code, organizadas por tecnología.
<br>
<a href="#skills-disponibles"><strong>Ver las skills »</strong></a>
<br>
<br>
<a href="https://github.com/dariomatias-dev/skills/issues">Reportar Bug</a>
·
<a href="https://github.com/dariomatias-dev/skills/issues">Solicitar Skill</a>
</p>

## Índice

- [Sobre el Proyecto](#sobre-el-proyecto)
- [Skills Disponibles](#skills-disponibles)
- [Estructura del Repositorio](#estructura-del-repositorio)
- [Instalación](#instalación)
- [Principios de Diseño](#principios-de-diseño)
- [Contribuir](#contribuir)
- [Licencia](#licencia)
- [Autor](#autor)

## Sobre el Proyecto

Una Agent Skill es una carpeta que contiene un archivo `SKILL.md` que enseña a un agente de código a trabajar en un contexto específico. El agente lee la descripción de la skill, determina si aplica a la tarea actual y carga las instrucciones antes de escribir código.

Este repositorio reúne skills que codifican convenciones de producción, no tutoriales: fronteras de arquitectura, reglas de nomenclatura, trampas específicas de bibliotecas que solo aparecen en tiempo de ejecución y el criterio de decisión detrás de cada elección.

Toda skill es **agnóstica del proyecto**. No contiene nombres de aplicación, entidades de dominio ni reglas de negocio, por lo que la misma skill se aplica a cualquier proyecto construido con esa tecnología.

## Skills Disponibles

### Flutter

Estructura feature-first, MVVM sobre Clean Architecture simplificada, Riverpod, rutas tipadas y Design System empaquetado. Índice completo en [flutter/README.md](flutter/README.md).

| Skill | Cubre |
| --- | --- |
| [flutter-architecture](flutter/flutter-architecture/) | Estructura, capas, anatomía de feature |
| [flutter-code-style](flutter/flutter-code-style/) | Nomenclatura, inmutabilidad, quality gates |
| [flutter-state-riverpod](flutter/flutter-state-riverpod/) | ViewModels, providers, ciclo de vida |
| [flutter-navigation](flutter/flutter-navigation/) | go_router, rutas tipadas, navigators |
| [flutter-design-system](flutter/flutter-design-system/) | Paquete de UI, tokens, componentes |
| [flutter-layout-insets](flutter/flutter-layout-insets/) | Safe areas, barras del sistema, teclado |
| [flutter-animation](flutter/flutter-animation/) | Controllers, rebuilds, rendimiento de motion |
| [flutter-data-layer](flutter/flutter-data-layer/) | Repositorios, elección de storage, errores |
| [flutter-database](flutter/flutter-database/) | Schema, índices, transacciones, migraciones |
| [flutter-networking](flutter/flutter-networking/) | Contrato HTTP, retry, refresh de token |
| [flutter-error-handling](flutter/flutter-error-handling/) | Fronteras de error, logging, reporte |
| [flutter-forms](flutter/flutter-forms/) | Controllers, validación, envío |
| [flutter-responsive-layout](flutter/flutter-responsive-layout/) | Breakpoints, estructura adaptativa |
| [flutter-testing](flutter/flutter-testing/) | Unitario, widget, golden, integración |
| [flutter-i18n](flutter/flutter-i18n/) | Archivos ARB, plurales, cambio de idioma |
| [flutter-project-setup](flutter/flutter-project-setup/) | Herramientas, lints, codegen, assets |
| [flutter-ci](flutter/flutter-ci/) | Pipeline, gate local, artefactos de release |
| [flutter-seed-data](flutter/flutter-seed-data/) | Datos de desarrollo, guarda de release |
| [flutter-screenshots](flutter/flutter-screenshots/) | Captura dirigida para listados |
| [flutter-release-notes](flutter/flutter-release-notes/) | Texto de listado en la tienda para un release |

### Markdown

Convenciones de documento válidas para cualquier repositorio, sea cual sea su tecnología. Índice completo en [markdown/README.md](markdown/README.md).

| Skill | Cubre |
| --- | --- |
| [markdown-readme](markdown/markdown-readme/) | Estructura de readme, badges, versiones traducidas |
| [markdown-community-health](markdown/markdown-community-health/) | Guía de contribución, política de seguridad |
| [markdown-architecture-doc](markdown/markdown-architecture-doc/) | Documento de arquitectura, capas, notas de decisión |

Otras tecnologías se incorporarán como carpetas separadas en la raíz.

## Estructura del Repositorio

```text
.
├── .claude-plugin/
│   └── marketplace.json             # lista un plugin por tecnología
├── flutter/
│   ├── .claude-plugin/
│   │   └── plugin.json              # hace instalable esta carpeta
│   ├── README.md                    # índice de la tecnología
│   ├── flutter-architecture/
│   │   └── SKILL.md
│   ├── flutter-design-system/
│   │   ├── SKILL.md
│   │   └── references/              # detalle profundo, cargado bajo demanda
│   └── ...
├── markdown/
│   ├── .claude-plugin/
│   ├── markdown-readme/
│   ├── markdown-community-health/
│   └── markdown-architecture-doc/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

Una carpeta por tecnología, una carpeta por skill. Una skill es un `SKILL.md` más un directorio `references/` opcional, para el material que no pertenece al archivo principal.

Cada carpeta de tecnología es un plugin autocontenido, por lo que instalar las skills de Flutter no incorpora skills de tecnologías que no están en uso.

## Instalación

Este repositorio es un **marketplace de plugins** de Claude Code. Cada tecnología se instala de forma independiente: el marketplace se registra una sola vez y cada tecnología requiere entonces un único comando.

```bash
claude plugin marketplace add dariomatias-dev/skills
claude plugin install flutter@dariomatias-dev
```

Reinicia Claude Code. Las veinte skills se cargan automáticamente y aparecen bajo el namespace del plugin, como en `flutter:flutter-architecture`.

| Tarea | Comando |
| --- | --- |
| Actualizar a la última versión | `claude plugin update flutter` |
| Inspeccionar los componentes cargados y su coste en tokens | `claude plugin details flutter` |
| Desactivar temporalmente | `claude plugin disable flutter` |
| Desinstalar | `claude plugin uninstall flutter` |

Solo las descripciones de las skills permanecen en el contexto, entre 70 y 90 tokens cada una. El cuerpo de la skill se lee únicamente cuando el agente determina que aplica a la tarea actual.

### Instalar una skill suelta

Para instalar skills individuales en lugar de una tecnología completa, crea un enlace simbólico para cada una de ellas:

```bash
git clone https://github.com/dariomatias-dev/skills.git
ln -sfn "$PWD/skills/flutter/flutter-architecture" ~/.claude/skills/flutter-architecture
```

Sustituye `~/.claude/skills/` por `<proyecto>/.claude/skills/` para limitar la skill a un solo proyecto.

### Otros agentes

Las skills siguen la [especificación abierta Agent Skills](https://agentskills.io/specification), y por lo tanto no están vinculadas a Claude Code. Cualquier agente que lea `SKILL.md` puede consumirlas directamente.

```bash
git clone https://github.com/dariomatias-dev/skills.git

# Codex, Cursor, Gemini CLI y otros: copia o vincula al directorio de skills del agente
cp -r skills/flutter/flutter-architecture <directorio-de-skills-del-agente>/
```

Para un proyecto que deba exponer las mismas skills a varios agentes, mantén una copia canónica y apunta los directorios de cada proveedor hacia ella, como hace el repositorio de Flutter:

```bash
mkdir -p .agents/skills
cp -r skills/flutter/* .agents/skills/
ln -s ../.agents/skills .claude/skills
```

Los manifiestos `.claude-plugin/` de este repositorio son aditivos. Los agentes que no los reconocen simplemente los ignoran.

## Principios de Diseño

Estas reglas mantienen la colección coherente a medida que crece:

| Principio | Por qué |
| --- | --- |
| Una regla vive en exactamente una skill | La guía duplicada se desincroniza y el agente recibe instrucciones contradictorias |
| La descripción dice qué cubre **y** cuándo usarla | La descripción es el único texto que el agente lee al decidir si carga la skill |
| Sin nombres específicos de proyecto | Una skill vinculada a una sola aplicación no es reutilizable y enseña la abstracción equivocada al agente |
| El detalle va a `references/` | Un `SKILL.md` largo cuesta contexto en cada carga; las references solo se leen cuando hacen falta |
| Las reglas explican el fallo que previenen | Un agente que comprende el modo de fallo aplica la regla en situaciones que el texto no enumera |

Las convenciones de autoría completas están documentadas en [CONTRIBUTING.md](CONTRIBUTING.md).

## Contribuir

Las contribuciones son bienvenidas, ya sea la corrección de una regla existente, una skill nueva o el soporte para una tecnología adicional.

Antes de abrir un pull request, consulta [CONTRIBUTING.md](CONTRIBUTING.md) para las convenciones de autoría, el formato de mensajes de commit (Conventional Commits) y las reglas de ramas que sigue este proyecto.

## Licencia

Distribuido bajo la Licencia MIT. Las skills pueden copiarse, adaptarse y usarse en
cualquier proyecto, incluidos los comerciales, siempre que se conserve el aviso de
copyright.

Consulta [LICENSE](LICENSE) para los términos completos.

## Autor

Desarrollado por **Dário Matias**:

- **Portafolio**: [dariomatias-dev](https://dariomatias-dev.com)
- **GitHub**: [dariomatias-dev](https://github.com/dariomatias-dev)
- **Correo**: [dariomatias.dev@gmail.com](mailto:dariomatias.dev@gmail.com)
- **Instagram**: [@dariomatias_dev](https://instagram.com/dariomatias_dev)
- **LinkedIn**: [linkedin.com/in/dariomatias-dev](https://linkedin.com/in/dariomatias-dev)
