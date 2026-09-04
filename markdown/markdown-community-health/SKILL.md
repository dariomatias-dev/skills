---
name: markdown-community-health
description: "Write and structure the community health files a repository carries beyond the readme: CONTRIBUTING and SECURITY. Use when writing or reviewing a contributing guide, a security policy, or deciding whether a rule belongs in one of these versus the README."
license: MIT
---

# Community Health Files

GitHub, GitLab and most forges treat CONTRIBUTING and SECURITY as a family: discovered automatically from the repository root, `docs/` or `.github/`, and surfaced from the Issues, pull request and security tabs without a manual link. Keep the two in one directory rather than splitting them across locations.

## Shared mechanics

Translated versions of any file in this family follow the same rules as `markdown-readme`'s Multi-language versions section: base file in English, `<name>.<locale>.md` per translation, locale order and code, a switcher at the top with the current language bold and unlinked, identical structure across languages. Apply those rules here without restating them.

## Contributing

What a contributor needs before opening a pull request, in the order they need it:

1. **Setup**: clone, install, generate, one pasteable block. If the project pins a toolchain version, say so and show the pinned command, not the bare one.
2. **Before opening a pull request**: a checklist, not prose. Link to where each rule actually lives (an architecture document, a design-system skill, a style guide) instead of restating it; a structural rule copied into CONTRIBUTING drifts from its source within a release.
3. **The local gate**: one command that runs what CI runs. If a technology-specific skill already documents that gate (a `flutter-ci` skill, for example), link to it instead of describing the command again.
4. **What CI checks**, as a table: job, what it does, and whether it gates the merge or only reports. A job list with no gate/report distinction leaves a contributor guessing which failure blocks them.
5. **Reproducing CI locally**, if the pipeline runs on a hosted runner: the tool and the one command that approximates it, and the caveat that a green local run is a signal, not a guarantee.
6. **Working with an AI agent**, if the repository carries agent configuration (a working-agreement file, a skills directory, hooks): link to each rather than duplicating it, and note that changing the agreement is a normal change, reviewed like any other.
7. **Dependency updates**: how an automated update pull request is triaged, and a link to a dependency-notes document if pins exist that are not obvious from the constraint alone.
8. **Commit and branch conventions**, linked or stated once.

```text
docs/
├── contributing.md
└── security.md
```

## Security policy

- **Supported versions**: a table or a sentence. A single-branch project can say so plainly instead of pretending a support matrix exists.
- **Reporting channel**: a private one. Prefer the forge's native private vulnerability reporting (GitHub's Security tab has one) over a bare email address, since it keeps the report and the fix out of the public tracker until disclosure; list an email as the fallback when the native tool is not enabled.
- **What to include in a report**: description and impact, reproduction steps, and the version or commit tested.
- **Response expectations, stated honestly**: a solo or hobby-maintained project has no SLA and should say so rather than promise one it cannot keep; commit only to acknowledging reports and crediting reporters, not to a response time.
- **Scope**: state plainly what classes of issue apply and which do not. A project with no server or account system should say so explicitly rather than leave it implied; a reporter otherwise wastes a report on a surface that does not exist.

## Boundaries

| Content | Lives in |
| --- | --- |
| What the project is, how to start | README |
| How to set up and submit a change | CONTRIBUTING |
| How to report a vulnerability privately | SECURITY |
| Where a file belongs, why a layer exists | `markdown-architecture-doc` |

## Anti-patterns

- A security policy promising a response time a solo maintainer cannot keep.
- Setup or structural rules duplicated between CONTRIBUTING and the README or the architecture document, which drift out of sync within a release.
- A CI table that lists jobs without marking which ones gate the merge.
- A public issue used to report a vulnerability, left open and disclosing it before a fix ships.
