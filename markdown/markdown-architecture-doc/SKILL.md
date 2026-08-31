---
name: markdown-architecture-doc
description: Write an architecture document that maps how a codebase is put together: layout, layering, boundaries and the non-obvious decisions behind them. Use when writing or reviewing an ARCHITECTURE document, a decision-note style file, or deciding whether a structural decision belongs in documentation or only in code.
license: MIT
---

# Architecture Documentation

One level deeper than the README's overview, aimed at anyone changing code: where a file belongs, why a layer exists, how the pieces talk to each other. Not a tutorial and not an API reference; both go stale faster than this document because they mirror implementation detail instead of decisions.

## Shape

- **Layout** as a directory tree that names roles, not every file. Collapse a level that repeats, such as one entry per feature or module, into a single annotated line rather than listing each one.
- **Layering or boundary rules** as prose right after the tree: what a layer is allowed to depend on, what is allowed to cross a boundary and what is not.
- **One section per subsystem with a non-obvious shape** (state management, persistence, error handling, an integration with an external service), each stating the decision and the reason, not an introduction to the library involved.
- **Links to source paths** instead of pasted code. A reader who needs the implementation opens the file; the document only needs to point at it.

## Decision notes

The part worth writing down is the part a reader could not infer from the code: why a dependency is pinned below its latest version, why a workaround exists, why two similar mechanisms were kept separate instead of merged. State the decision, the constraint that forced it, and what removes the constraint, so a future contributor does not "fix" it without knowing what breaks.

A pin or a workaround with no recorded reason gets undone by whoever hits it next. Write the reason once, in this document or in a dedicated notes file it links to, and it stops being re-litigated.

## Keeping it truthful

- Describe the system as it is, never as it is planned to be. A "not yet implemented" note belongs in an issue, not here.
- Whoever changes a layering rule, a boundary, or a subsystem this document covers updates the document in the same change, not a follow-up.
- A stale architecture document is worse than none: it sends a contributor to the wrong layer with full confidence.
- When a technology-specific skill already states a structural rule for an agent (a layering rule, a naming convention), this document may restate it briefly for a human reader, but the skill stays the source of truth. A rule that exists only here goes unenforced.

## Boundaries

| Content | Lives in |
| --- | --- |
| What the project is, how to start | README |
| Where a file belongs, why a layer exists | This document |
| How to set up and submit a change | `markdown-community-health` |
| Rules an agent must follow while writing code | The technology's own skill |

## Anti-patterns

- A full source tree pasted in, one line per file: outdated the moment a file is added.
- Tutorial prose explaining what a well-known library does, instead of how this project uses it.
- A decision recorded with no reason, so it reads as arbitrary and gets reverted by someone who did not know why it existed.
- This document and a technology skill stating the same layering rule in different wording, so the two drift and contradict each other.
