# Kickstart

Kickstart turns a few plain-English project-start answers into a practical kickoff packet:

- `PROJECT.md` for stable project context
- `TASKS.md` for initial execution state
- `KICKOFF.md` for the first structured assistant instruction

The first two questions set the branch:

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

By default, existing files are not overwritten. Use `--force` only when replacing generated files is intentional.

## Validate

```bash
PYTHONPATH=src python3 -m unittest discover -s tests
```
