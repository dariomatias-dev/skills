---
name: markdown-readme
description: Structure a repository readme that reads as a product page: header block, section order, badges, installation, multi-language versions and the boundary with the other documents a project carries. Use when writing or reviewing a README, adding a translated version, or deciding which document a piece of documentation belongs in.
license: MIT
---

# Repository Readme

A readme answers three questions in order: what this is, whether it fits my problem, and how to start. Everything else is secondary, and anything that answers none of them belongs in another file.

## Header block

Before the first heading, centered:

1. Badges, four or five at most.
2. Language switcher, if translations exist.
3. Project name as `<h1>`.
4. One sentence stating what the project is.
5. Primary link into the document, then links to report a bug and request a feature.

```html
<p align="center">
<strong>English</strong> · <a href="README.es.md">Español</a> · <a href="README.pt-BR.md">Português (BR)</a>
</p>
```

Rules:

- Badges carry state, not decoration: version, license, build, coverage. A badge for something with no state is noise.
- Give every badge alt text that includes the value, not just the label. `License: MIT`, not `License`. Without it the information is invisible to screen readers and to any renderer that does not load images.
- Never show a badge for a pipeline that does not exist. A permanently grey or broken badge is worse than none.
- Keep the name a name. The sentence underneath is where the explanation goes.

## Section order

| Section | Contains |
| --- | --- |
| Table of contents | Every second-level heading, once the document passes roughly three screens |
| About | What the project is, the problem it solves, the decision that makes it different |
| Features or contents | What is inside, as a table when the list has structure |
| Installation | The shortest path from nothing to running |
| Usage | The smallest complete example, then a link to deeper docs |
| Configuration | Only what a user must set; defaults belong in reference docs |
| Contributing | Two sentences and a link to CONTRIBUTING.md |
| License | One sentence in prose, plus the link |
| Author | Name and contact links |

Delete sections that do not apply rather than filling them. An empty Screenshots heading reads as an abandoned project.

## Installation

- Show the commands, in order, in one block that can be pasted.
- State prerequisites before the commands, not after the reader has failed.
- If there are several installation paths, lead with the one most readers need and put the rest under sub-headings.
- Verify the copied commands actually run in a clean environment. A readme that fails at step one is the most expensive bug in the repository.

## Multi-language versions

- `README.md` is the base language. Translations are `README.<locale>.md`, using the locale code, not the language name.
- List locales in code order, `en`, `es`, `pt-BR`, so the sequence stays predictable as more are added.
- The switcher appears at the top of every version, with the current language in bold and unlinked.
- Translate the prose, never the commands, file names or code.
- Keep the section structure identical across versions. A translation that drifts structurally becomes impossible to review.
- A stale translation is worse than a missing one: it states things that are no longer true with the same confidence.

## Documents beyond the readme

Once a project carries more than a readme, the rest belong in `docs/`, translated the same way:

```text
README.md              README.es.md              README.pt-BR.md
docs/
├── architecture.md    architecture.es.md        architecture.pt-BR.md
├── contributing.md    contributing.es.md        contributing.pt-BR.md
├── dependencies.md    dependencies.es.md        dependencies.pt-BR.md
└── security.md        security.es.md            security.pt-BR.md
```

The readme stays the entry point and links into them. Moving a document into `docs/` is what keeps the readme readable as the project grows. What belongs inside the architecture document is covered by `markdown-architecture-doc`; what belongs inside contributing and security is covered by `markdown-community-health`. This skill only covers the readme itself and where a document lives.

## Keeping documentation true

Documentation rots because updating it is treated as a separate task. Make it part of the change that invalidated it, and state explicitly what invalidates what:

| Change | Update |
| --- | --- |
| A user-visible capability | Readme, every language |
| A structural convention or layer boundary | The architecture document |
| The workflow, checks or tooling | The contributing document |
| A dependency added, removed or pinned | The dependency document, and the reason for the pin |
| A script's name or behavior | The readme's script table |
| A number the readme quotes, such as a threshold | The readme |

A document updated in one language and not the others is a broken change, not a partial one. The stale versions keep asserting the old behavior with full confidence, and the readers who need them least are the ones reading the language you updated.

Prefer documenting a fact in one place and linking to it. A number repeated in the readme, the contributing guide and a workflow file will be wrong in at least one of them within two releases.

## Boundaries with other files

| Content | File |
| --- | --- |
| How to use the project | README |
| How to set up and submit a change | CONTRIBUTING |
| How to report a vulnerability | SECURITY |
| Where a file belongs, why a layer exists | An architecture document |
| What changed per version | CHANGELOG |
| Legal terms | LICENSE |

The readme links to each; it does not restate them. Setup instructions duplicated in both README and CONTRIBUTING drift within two releases. CONTRIBUTING and SECURITY follow `markdown-community-health`; an architecture document follows `markdown-architecture-doc`.

## Writing

- Write for someone who arrived from a search result and knows nothing about the project.
- Prefer tables to paragraphs for anything the reader scans rather than reads.
- State facts, not enthusiasm. Adjectives about how powerful or elegant something is convince nobody and date badly.
- Every code block should be runnable as written, with placeholders that are obviously placeholders.
- Keep line-level formatting plain: no typographic dashes or quotes, since readme text gets copied into terminals, issues and package registries.

## Anti-patterns

- Boilerplate from a template left unedited, such as generic paragraphs about the open-source community.
- A wall of badges, several reporting the same fact.
- A features list that reads as marketing rather than contents.
- Installation instructions that assume a working environment the reader does not have.
- Screenshots that no longer match the current interface.
- A table of contents on a document short enough to read without one.
- Links to sections that were renamed, which break silently.
