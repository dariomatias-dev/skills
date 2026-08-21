<br>
<div align="center">
<img src="https://img.shields.io/badge/Agent%20Skills-20-informational?style=for-the-badge" alt="Agent Skills">
<img src="https://img.shields.io/badge/Claude%20Code-compatible-D97757?style=for-the-badge&logo=anthropic&logoColor=white" alt="Claude Code">
<img src="https://img.shields.io/badge/Flutter-covered-02569B?style=for-the-badge&logo=flutter&logoColor=white" alt="Flutter">
<img src="https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge" alt="License: MIT">
</div>
<br>

<p align="center">
<strong>English</strong> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português (BR)</a>
</p>

<h1 align="center">Agent Skills</h1>

<p align="center">
Production-grade <strong>Agent Skills</strong> for Claude Code, organized by technology.
<br>
<a href="#available-skills"><strong>Browse the skills »</strong></a>
<br>
<br>
<a href="https://github.com/dariomatias-dev/skills/issues">Report Bug</a>
·
<a href="https://github.com/dariomatias-dev/skills/issues">Request Skill</a>
</p>

## Table of Contents

- [About the Project](#about-the-project)
- [Available Skills](#available-skills)
- [Repository Structure](#repository-structure)
- [Installation](#installation)
- [Design Principles](#design-principles)
- [Contributing](#contributing)
- [License](#license)
- [Author](#author)

## About the Project

An Agent Skill is a folder containing a `SKILL.md` file that teaches a coding agent how to work in a specific context. The agent reads the skill's description, determines whether it applies to the current task, and loads the instructions before writing any code.

This repository collects skills that encode production conventions rather than tutorials: architecture boundaries, naming rules, library-specific pitfalls that only surface at runtime, and the decision criteria behind each choice.

Every skill is **project-agnostic**. It contains no application names, domain entities or business rules, so the same skill applies to any project built with that technology.

## Available Skills

### Flutter

Feature-first structure, MVVM over a simplified Clean Architecture, Riverpod, typed routing and a packaged design system. Full index in [flutter/README.md](flutter/README.md).

| Skill | Covers |
| --- | --- |
| [flutter-architecture](flutter/flutter-architecture/) | Structure, layers, feature anatomy |
| [flutter-code-style](flutter/flutter-code-style/) | Naming, immutability, quality gates |
| [flutter-state-riverpod](flutter/flutter-state-riverpod/) | ViewModels, providers, lifecycle |
| [flutter-navigation](flutter/flutter-navigation/) | go_router, typed routes, navigators |
| [flutter-design-system](flutter/flutter-design-system/) | UI package, tokens, components |
| [flutter-layout-insets](flutter/flutter-layout-insets/) | Safe areas, system bars, keyboard |
| [flutter-animation](flutter/flutter-animation/) | Controllers, rebuilds, motion performance |
| [flutter-data-layer](flutter/flutter-data-layer/) | Repositories, storage choice, errors |
| [flutter-database](flutter/flutter-database/) | Schema, indexes, transactions, migrations |
| [flutter-networking](flutter/flutter-networking/) | HTTP contract, retry, token refresh |
| [flutter-error-handling](flutter/flutter-error-handling/) | Error boundaries, logging, reporting |
| [flutter-forms](flutter/flutter-forms/) | Controllers, validation, submission |
| [flutter-responsive-layout](flutter/flutter-responsive-layout/) | Breakpoints, adaptive structure |
| [flutter-testing](flutter/flutter-testing/) | Unit, widget, golden, integration |
| [flutter-i18n](flutter/flutter-i18n/) | ARB files, plurals, locale switching |
| [flutter-project-setup](flutter/flutter-project-setup/) | Tooling, lints, codegen, CI/CD |
| [flutter-seed-data](flutter/flutter-seed-data/) | Development data, release guard |
| [flutter-screenshots](flutter/flutter-screenshots/) | Driven capture for listings |
| [flutter-release-notes](flutter/flutter-release-notes/) | Store listing text for a release |

### Markdown

Document conventions that apply to any repository, regardless of its technology. Full index in [markdown/README.md](markdown/README.md).

| Skill | Covers |
| --- | --- |
| [markdown-readme](markdown/markdown-readme/) | Readme structure, badges, translated versions |

Additional technologies will be added as separate top-level folders.

## Repository Structure

```text
.
├── .claude-plugin/
│   └── marketplace.json             # lists one plugin per technology
├── flutter/
│   ├── .claude-plugin/
│   │   └── plugin.json              # makes this folder installable
│   ├── README.md                    # technology index
│   ├── flutter-architecture/
│   │   └── SKILL.md
│   ├── flutter-design-system/
│   │   ├── SKILL.md
│   │   └── references/              # deep detail, loaded on demand
│   └── ...
├── markdown/
│   ├── .claude-plugin/
│   └── markdown-readme/
├── CONTRIBUTING.md
├── LICENSE
└── README.md
```

One folder per technology, one folder per skill. A skill is a `SKILL.md` plus an optional `references/` directory for material that does not belong in the main file.

Each technology folder is a self-contained plugin, so installing the Flutter skills does not bring in skills for technologies that are not in use.

## Installation

This repository is a Claude Code **plugin marketplace**. Each technology is installed independently: the marketplace is registered once, and each technology then requires a single command.

```bash
claude plugin marketplace add dariomatias-dev/skills
claude plugin install flutter@dariomatias-dev
```

Restart Claude Code. The nineteen skills are loaded automatically and appear under the plugin namespace, as in `flutter:flutter-architecture`.

| Task | Command |
| --- | --- |
| Update to the latest version | `claude plugin update flutter` |
| Inspect the components loaded and their token cost | `claude plugin details flutter` |
| Disable it temporarily | `claude plugin disable flutter` |
| Uninstall it | `claude plugin uninstall flutter` |

Only the skill descriptions remain in context permanently, roughly 70 to 90 tokens each. The body of a skill is read only when the agent determines that it applies to the current task.

### Installing a single skill

To install individual skills rather than an entire technology, create a symbolic link for each one required:

```bash
git clone https://github.com/dariomatias-dev/skills.git
ln -sfn "$PWD/skills/flutter/flutter-architecture" ~/.claude/skills/flutter-architecture
```

Replace `~/.claude/skills/` with `<project>/.claude/skills/` to limit a skill to a single project.

### Other agents

The skills follow the open [Agent Skills specification](https://agentskills.io/specification), and are therefore not tied to Claude Code. Any agent that reads `SKILL.md` can consume them directly.

```bash
git clone https://github.com/dariomatias-dev/skills.git

# Codex, Cursor, Gemini CLI and others: copy or link into the agent's skills directory
cp -r skills/flutter/flutter-architecture <agent-skills-dir>/
```

For a project that should expose the same skills to several agents, keep one canonical copy and point the vendor directories at it, as the Flutter repository does:

```bash
mkdir -p .agents/skills
cp -r skills/flutter/* .agents/skills/
ln -s ../.agents/skills .claude/skills
```

The `.claude-plugin/` manifests in this repository are additive. Agents that do not recognize them ignore them.

## Design Principles

These rules keep the collection coherent as it grows:

| Principle | Why |
| --- | --- |
| One rule lives in exactly one skill | Duplicated guidance drifts out of sync and the agent receives contradictory instructions |
| Descriptions state coverage **and** trigger | The description is the only text the agent reads when deciding whether to load the skill |
| No project-specific names | A skill tied to a single application cannot be reused and teaches the agent the wrong abstraction |
| Detail goes to `references/` | A long `SKILL.md` costs context on every load; references are read only when needed |
| Rules explain the failure they prevent | An agent that understands the failure mode applies the rule in situations the text does not enumerate |

The complete authoring conventions are documented in [CONTRIBUTING.md](CONTRIBUTING.md).

## Contributing

Contributions are welcome, whether a correction to an existing rule, a new skill, or support for an additional technology.

Before opening a pull request, review [CONTRIBUTING.md](CONTRIBUTING.md) for the authoring conventions, the commit message format (Conventional Commits), and the branching rules this project follows.

## License

Distributed under the MIT License. The skills may be copied, adapted and used in
any project, including commercial ones, as long as the copyright notice is kept.

See [LICENSE](LICENSE) for the full terms.

## Author

Developed by **Dário Matias**:

- **Portfolio**: [dariomatias-dev](https://dariomatias-dev.com)
- **GitHub**: [dariomatias-dev](https://github.com/dariomatias-dev)
- **Email**: [dariomatias.dev@gmail.com](mailto:dariomatias.dev@gmail.com)
- **Instagram**: [@dariomatias_dev](https://instagram.com/dariomatias_dev)
- **LinkedIn**: [linkedin.com/in/dariomatias-dev](https://linkedin.com/in/dariomatias-dev)
