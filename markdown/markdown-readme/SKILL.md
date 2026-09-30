---
name: markdown-readme
description: "Structure a repository readme that reads as a product page: header block, fixed section order across five blocks, badges, getting started, multi-language versions and the boundary with the other documents a project carries. Use when writing or reviewing a README, adding a translated version, or deciding which document a piece of documentation belongs in."
license: MIT
---

# Repository Readme

A readme answers three questions in order: what this is, whether it fits my problem, and how to start. Everything that answers none of them is reference material and comes after. That is why sections group into five blocks, from the hook to the legal footer.

## Block 1 — Header (before the first heading)

Give the name, the project's health, and the language in five seconds. This is what shows on the GitHub card and in search results.

| Element           | Answers                    | Rule                                                                                                               |
| ----------------- | -------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| Technology badges | "what is it built with?"   | 3 to 5, `style=for-the-badge`. Only what defines the project; framework yes, utility no                            |
| Status badges     | "is it alive and healthy?" | CI, coverage, license, minimum platform version. Each with `alt` text that includes the value (`License: MIT`)     |
| Language switcher | "is it in my language?"    | fixed order `en · es · pt-BR · zh`; current language in bold, unlinked                                             |
| Title             | "what is it called?"       | `<h1 align="center">`, name only; the explanation goes below                                                       |
| One-line summary  | "what is it?"              | one sentence, no marketing adjectives. This is the text that gets copied into the repository's `description` field |
| Action links      | "where do I start?"        | `Explore the docs »` → `#about-the-project`, then `Report Bug` and `Request Feature`                               |

**Does not belong here:** an intro paragraph, an oversized logo, a badge for something with no state (zero downloads, "made with love").

## Block 2 — Core (the reader decides whether to stay)

### `Table of Contents`

**Answers:** "what does this document cover?" · **When:** whenever the document passes roughly three screens · **Contains:** one entry per `##`, in exact order · **Does not belong here:** `###` subheadings, which make the list unreadable.

### `About the Project`

**Answers:** "what is it, what problem does it solve, why does it exist?" · **When:** always · **Contains:** 2 to 4 short paragraphs: what it is; the decision that makes it different; where it is published (site, store); and what this repository does **not** contain, when sibling repositories exist · **Length:** up to ~10 lines · **Does not belong here:** personal history, a feature list (that has its own section).

### `Preview`

**Answers:** "what does this look like?" · **When:** the project has a user interface · **Contains:** 1 to 3 images or a GIF, each with a one-line caption; placed early because an image convinces faster than text · **Does not belong here:** a gallery of nine images, or a stale screenshot (worse than none).

### `Features`

**Answers:** "does it do what I need?" · **When:** always · **Contains:** a list of what exists today, verifiable, one line per item, leading with what is unusual · **Does not belong here:** future plans (that is a roadmap), marketing adjectives ("powerful", "modern"), or implementation detail (that belongs in architecture).

### Domain section (optional, at most one)

**Answers:** the question specific to that project — "what's in the catalog?" (`The App`), "how do I write content?" (`Content`) · **When:** there is a central concept that does not fit in Features or Architecture · **Why cap at one:** every extra section pushes `Getting Started` further down, and that is where the reader actually wants to get to.

## Block 3 — Usage (the reader leaves here running)

### `Tech Stack`

**Answers:** "will I be able to work on this?" · **Contains:** the main choices grouped by role (framework, styling, state, testing, tooling) · **Does not belong here:** a dump of `package.json`/`pubspec.yaml`, which goes stale in a week.

### `Architecture`

**Answers:** "where does each thing live?" · **When:** `docs/architecture.md` exists · **Contains:** 3 to 5 lines with the structural rule and what enforces it (e.g. a lint rule that blocks cross-feature imports), plus the link · **Does not belong here:** the full explanation, that lives in the document, and duplicating it guarantees drift.

### `Getting Started`

**Answers:** "how do I go from zero to running?" · **Contains:** prerequisites **before** the commands, then a single pasteable block that ends with the app running; environment variables referenced alongside their example file · **Rule:** the commands must work in a clean environment; a readme that fails at step one is the most expensive bug in the repository · **Does not belong here:** contribution instructions (that is `CONTRIBUTING`).

### `Scripts`

**Answers:** "what can I run?" · **When:** scripts exist · **Format:** command/description table, in order of use (dev → build → quality) · **Does not belong here:** internal scripts nobody calls by hand.

### `Testing`

**Answers:** "is this reliable, and how do I check?" · **Contains:** the test types, the command for each, the local gate equivalent to CI, and what it blocks · **Does not belong here:** a list of test cases; coverage numbers should live in a single place, preferably the badge.

## Block 4 — Project (whoever contributes or operates it)

### `Deployment`

**Answers:** "how does this reach production?" · **When:** the project is published somewhere (hosting, store) · **Contains:** where it runs, what blocks a merge, how the version is generated and published.

### `Documentation`

**Answers:** "where's the rest?" · **When:** `docs/` exists · **Format:** a document/what-it-covers table, acting as an index so the readme does not bloat · **Rule:** each row points to the version in that readme's own language.

### `Contributing`

**Answers:** "how do I help?" · **Contains:** two sentences, the local gate command, and a link to `CONTRIBUTING.md`.

### `Security`

**Answers:** "I found a flaw, now what?" · **When:** a policy exists · **Contains:** one sentence saying not to open a public issue, plus the link to the policy.

## Block 5 — Footer

### `License`

**Answers:** "can I use this?" · **Contains:** one prose sentence naming the license, plus the link to the file.

### `Author`

**Answers:** "who maintains this?" · **Contains:** name and contacts, always in the same order: portfolio, GitHub, email, Instagram, LinkedIn.

## Cross-cutting rules

- **Fixed section names**, so anchors match across every repository: `About the Project`, `Preview`, `Features`, `Tech Stack`, `Architecture`, `Getting Started`, `Scripts`, `Testing`, `Deployment`, `Documentation`, `Contributing`, `Security`, `License`, `Author`.
- **Missing sections are omitted, never left empty.** A heading with no content under it reads as an abandoned project.
- **One fact, one place.** A number repeated across the readme, the contributing guide and a workflow file will be wrong in at least one of them within two releases.
- **Translations are structurally identical:** same number and order of sections. Translate the prose only, never commands, file names, or code.
- **Updating the readme is part of the change that invalidated it**, in all three languages, not a separate task.
- **Flat formatting:** no typographic dashes, no curly quotes — this text gets copied into terminals, issues and registries.

## Skeleton

```markdown
<header: technology badges, status badges, languages, title, sentence, links>

## Table of Contents

## About the Project

## Preview <!-- if there's a user interface -->

## Features

## <Domain section> <!-- at most one, optional -->

## Tech Stack

## Architecture <!-- if docs/architecture.md exists -->

## Getting Started

## Scripts

## Testing

## Deployment <!-- if published somewhere -->

## Documentation <!-- if docs/ exists -->

## Contributing

## Security <!-- if a policy exists -->

## License

## Author
```

## Multi-language versions

- `README.md` is the base language (English). Translations are `README.<locale>.md`, using the locale code, not the language name.
- Switcher order is fixed: `en · es · pt-BR · zh`. The current language is bold and unlinked.
- Translate the prose, never the commands, file names or code.
- Keep section structure identical across versions. A translation that drifts structurally becomes impossible to review.
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

## Boundaries with other files

| Content                                  | File                     |
| ---------------------------------------- | ------------------------ |
| How to use the project                   | README                   |
| How to set up and submit a change        | CONTRIBUTING             |
| How to report a vulnerability            | SECURITY                 |
| Where a file belongs, why a layer exists | An architecture document |
| What changed per version                 | CHANGELOG                |
| Legal terms                              | LICENSE                  |

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
- More than one domain section, pushing Getting Started too far down.
