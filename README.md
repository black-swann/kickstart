# Kickstart

Kickstart turns a few plain-English project-start answers into a practical kickoff packet:

- `PROJECT.md` for stable project context
- `TASKS.md` for initial execution state
- `KICKOFF.md` for the first structured assistant instruction

It is a dependency-light Python CLI for shaping rough ideas into enough context for the next implementation pass.

## Features

- Guided interview for new projects or existing repositories
- Keyboard-friendly terminal menus with a review step before generation
- Preview mode by default
- Safer write mode that refuses accidental overwrites
- Existing-repo snapshot support for common project files, current branch, and dirty state
- No runtime third-party dependencies

The first prompts set the branch:

1. Are you starting a new project, or working inside an existing repo?
2. Should the tool preview generated files first, or write them directly?

The next prompts collect project context, then apply a quality preset:

- prototype
- production
- learning
- repo cleanup
- custom

You can also choose concise or detailed kickoff guidance.

The question flow is intentionally beginner-friendly. If you do not know the tech stack, choose "Suggest one for me" and Kickstart will tell the generated kickoff brief to compare stack choices in plain English.

In an interactive terminal, choice prompts support:

- Up/Down arrows or `j`/`k` to move
- number keys to jump to an option
- Enter to select
- `q`, Escape, or Ctrl-C to quit

Before generating files, Kickstart shows a review panel. You can confirm, go back through the answers, or quit without generating anything.

## Security Notes

Kickstart does not require network access and does not execute generated files. Existing-repo inspection runs read-only `git` commands through `subprocess.run()` without a shell.

Generated files can include the repository path, constraints, risks, and other context you type into the prompts. Review generated output before committing it to a public repository.

## Prompt Model

Kickstart follows a simple research-backed structure used across major prompt guidance:

- task: what you want to make
- audience: who it is for
- context: constraints, risks, and current repo state
- success: what finished means
- output format: concise or detailed kickoff guidance

References:

- OpenAI: https://help.openai.com/en/articles/6654000-best-practices-for-prompt-en
- Microsoft Learn: https://learn.microsoft.com/en-us/azure/ai-services/openai/concepts/prompt-engineering
- Google Cloud: https://docs.cloud.google.com/vertex-ai/generative-ai/docs/learn/prompt-best-practices

## Run

```bash
PYTHONPATH=src python3 -m kickstart init
```

For regular local use, install it in editable mode:

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install -e .
kickstart init
```

Preview mode is the default. To write files directly:

```bash
PYTHONPATH=src python3 -m kickstart init --write --output-dir ./example-output
```

For an existing repo:

```bash
PYTHONPATH=src python3 -m kickstart init --project-type existing --repo-path /path/to/repo
```

By default, existing files are not overwritten. If `--write` would replace generated files in an interactive terminal, Kickstart shows the conflicting paths and lets you preview instead, overwrite, or quit. In non-interactive runs, it refuses to overwrite unless `--force` is set.

Use `--force` only when replacing generated files is intentional:

```bash
PYTHONPATH=src python3 -m kickstart init --write --force --output-dir ./example-output
```

## Validate

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
python3 -m compileall -q src tests
```

Before making a release or changing repository visibility, also run a hygiene scan over the current tree and reachable history for local paths, secrets, and private workflow files.
