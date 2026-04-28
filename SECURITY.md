# Security Policy

## Supported Versions

Kickstart is pre-1.0. Security fixes are applied to the latest commit on `main`.

## Reporting A Vulnerability

Please report suspected vulnerabilities through GitHub private vulnerability reporting when available, or open an issue with a minimal description that avoids sharing secrets publicly.

Include:

- the affected command or generated file
- the operating system and Python version
- steps to reproduce
- why the behavior could expose data, overwrite files, or execute unintended commands

## Security Model

Kickstart is a local CLI. It does not require network access, and it does not execute generated files.

Existing-repo inspection is read-only and uses `git` through `subprocess.run()` without a shell. Write mode only writes the generated `PROJECT.md`, `TASKS.md`, and `KICKOFF.md` files, refuses overwrites by default, and requires an explicit overwrite choice or `--force`.

Generated output may include user-provided context and local repository paths. Review generated files before committing or publishing them.
