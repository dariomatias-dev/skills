# Contributing

Contributions are welcome, whether a fix to an existing rule, a new skill, or a new technology folder.

## Table of Contents

- [Repository Layout](#repository-layout)
- [Writing a Skill](#writing-a-skill)
- [Adding a Technology](#adding-a-technology)
- [Local Setup](#local-setup)
- [Commit Convention](#commit-convention)
- [Branching](#branching)
- [Pull Requests](#pull-requests)

## Repository Layout

The repository root is a plugin marketplace. Each technology folder is one installable plugin.

```text
.claude-plugin/
└── marketplace.json              # one entry per technology

<technology>/
├── .claude-plugin/
│   └── plugin.json               # "skills": ["./"] keeps skills at this level
├── README.md                     # index for that technology
└── <technology>-<topic>/
    ├── SKILL.md                  # required
    └── references/               # optional
```

The skill folder name matches the `name` in the frontmatter and carries the technology prefix, so a listing of many skills stays readable and two technologies can cover the same topic without colliding.

Repository-wide tooling sits outside any technology folder: `scripts/` holds the local verification gate, `.github/workflows/` runs it in CI, and `.githooks/` holds the commit message hook. See [Local Setup](#local-setup) and [Commit Convention](#commit-convention).

## Writing a Skill

### Frontmatter

```markdown
---
name: flutter-navigation
description: Typed navigation with go_router and go_router_builder: route classes, per-feature navigators, shell routes, redirects and transitions. Use when adding or changing a route, wiring tab shells, guarding access, customizing page transitions, or fixing go_router_builder generation errors.
license: MIT
---
```

Skills follow the open [Agent Skills specification](https://agentskills.io/specification), which is vendor-neutral. Keep them compliant so any agent can consume them:

| Field | Rule |
| --- | --- |
| `name` | 1 to 64 characters, lowercase letters, digits and single hyphens, must match the folder name |
| `description` | 1 to 1024 characters, states coverage and trigger |
| `license` | `MIT`, so a skill stays self-describing when copied on its own |

The body should stay under 500 lines, with deeper material in `references/`. Validate with the reference tooling:

```bash
npx skills-ref validate ./flutter/<skill-name>
```

`description` is the single most important line in the file. It is the only text the agent reads when deciding whether to load the skill, so it must state two things:

1. **What the skill covers**, in concrete nouns.
2. **When to use it**, as the situations that should trigger it.

A description that only names the topic gets the skill loaded at the wrong times, or not at all.

### Body rules

- **One rule, one skill.** Before adding a rule, search the other skills for it. If it already exists elsewhere, link to that skill instead of restating it. Duplicated guidance drifts apart and produces contradictory instructions.
- **Project-agnostic.** No application names, domain entities or business rules. Use neutral placeholders (`Item`, `<feature>`). A skill that mentions one product teaches the wrong abstraction.
- **State the failure, not just the rule.** "Bumping `schemaVersion` without a migration fails silently for users with the old database installed" generalizes to cases the text never listed; "always write migrations" does not.
- **Prefer tables and lists over prose** for anything the agent must scan and match against a situation.
- **Show real code**, short and compilable in shape. No pseudo-code, no `// ...` standing in for the part that matters.
- **Include the anti-patterns.** Knowing what not to write is as actionable as knowing what to write.
- **Keep `SKILL.md` focused.** It is loaded in full every time the skill triggers, so it costs context. Long catalogs, exhaustive scales and deep reference material go into `references/`, linked from the body and read only when needed.

### Style

- Write in English.
- No typographic dashes or ellipsis characters. Use `.`, `:`, `;`, `,` or parentheses. Skill text is a prompt, and its punctuation habits leak into the code comments, commit messages and documentation the agent later writes.
- Be direct. Cut hedging and filler.

## Adding a Technology

1. Create a top-level folder named after the technology.
2. Add `<technology>/.claude-plugin/plugin.json` with `"skills": ["./"]`, a semver `version`, and a description listing what the plugin covers.
3. Register it in `.claude-plugin/marketplace.json` with `"source": "./<technology>"`.
4. Add a `README.md` inside the folder: a table of the skills, a suggested reading order, and the boundary between them (which skill owns which kind of rule).
5. Add the skills, each in its own folder with the technology prefix.
6. Add a section for the technology in the root `README.md` and its translations.
7. Run `claude plugin validate .` and confirm the manifest passes.

## Local Setup

Install the marketplace from your local clone, so edits take effect without pushing anything:

```bash
git clone https://github.com/dariomatias-dev/skills.git
cd skills

claude plugin marketplace add "$PWD"
claude plugin install <technology>@dariomatias-dev
```

After editing a skill, refresh and confirm it is picked up:

```bash
claude plugin marketplace update dariomatias-dev
claude plugin details <technology>
```

`details` lists every skill the plugin exposes and its token cost. A skill missing from that list is a discovery problem, usually a malformed frontmatter or a folder in the wrong place.

Before opening a pull request, verify the skill actually triggers: start a session in a project of that technology, describe a task the skill should cover, and confirm it loads and that the guidance holds up against real code.

When you are done, point the marketplace back at the published repository:

```bash
claude plugin marketplace remove dariomatias-dev
claude plugin marketplace add dariomatias-dev/skills
```

### The local gate

`./scripts/verify.sh` runs everything CI runs: marketplace and plugin manifest consistency, every `SKILL.md` against the Agent Skills spec, README translation structure, and local markdown links. Run it before opening a pull request; a check that only exists in CI is found after the push, by whoever is waiting on the review.

```bash
./scripts/verify.sh
```

## Commit Convention

This project follows [Conventional Commits](https://www.conventionalcommits.org/).

```text
<type>(<scope>): <subject>
```

| Type | Use for |
| --- | --- |
| `feat` | New skill, new section, new rule |
| `fix` | Wrong, outdated or misleading guidance |
| `docs` | READMEs, contributing, translations |
| `refactor` | Reorganizing content with no change in meaning |
| `chore` | Tooling, licensing, repository files |

The scope is the skill or technology: `feat(flutter-navigation): document shell route Hero collision`.

Subject in the imperative, no trailing period. Add a body when the reasoning is not obvious from the subject.

## Branching

Branch from `main`, named `<type>/<short-description>`:

```text
feat/flutter-accessibility-skill
fix/riverpod-autodispose-guard
docs/es-translation
```

## Pull Requests

- One logical change per pull request.
- State which skills the change touches and why the rule belongs there rather than in a neighboring skill.
- For a rule that documents a real failure, describe the failure you hit.
- For a new skill, include the reasoning behind its boundary: what it owns, and what it deliberately leaves to other skills.
