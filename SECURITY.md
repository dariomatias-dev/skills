# Security Policy

## Supported versions

This repository has a single supported line: the `main` branch. Fixes land there, and there are no maintenance branches for older tags.

## Scope

This repository ships Markdown instructions for coding agents, plus the scripts that validate them. That shapes what is worth reporting:

| In scope | Example |
| --- | --- |
| Guidance that leads an agent to write insecure code | A rule that stores credentials in plain key-value storage, disables certificate validation, or logs tokens |
| Instructions that could redirect an agent's behavior | Text in a skill that an agent would follow as a command rather than read as guidance |
| A vulnerability in the repository's own tooling | Command injection or arbitrary file write in `scripts/`, the commit hook, or a workflow |
| Supply chain exposure in the workflows | An unpinned or compromised action that can reach repository secrets |

| Out of scope | Reason |
| --- | --- |
| Bugs in Flutter, Dart, Claude Code or any third-party package named by a skill | Report those upstream |
| Disagreement with a technical recommendation | Open a normal issue or pull request; that is a correctness discussion, not a vulnerability |
| Findings from an automated scanner with no demonstrated impact here | This repository has no server, no accounts, no user data and executes nothing at install time |

There is no hosted service, no account system and no user data behind this project.

## Reporting a vulnerability

Report privately, through GitHub's private vulnerability reporting on this repository's **Security** tab ("Report a vulnerability"). It keeps the report and the fix out of the public tracker until disclosure.

Never open a public issue for a vulnerability, and never include a working exploit against a third party in the report.

Include:

- a description of the issue and its impact;
- the steps to reproduce it, and the file or skill it affects;
- the commit tested;
- anything that limits the impact, if you know of it.

## What to expect

This project is maintained by one person, in the open, with no service level agreement. What is committed to:

- reports are acknowledged;
- accepted findings are fixed on `main` and the reporter is credited, unless they ask not to be.

No response time is promised, because none could be kept honestly.
