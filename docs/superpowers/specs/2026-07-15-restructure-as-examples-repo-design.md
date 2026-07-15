# Restructure Repo as Multi-Example Collection — Design Spec

**Date:** 2026-07-15
**Project:** `agent-examples` (new repo name, replaces `a2a-maf`)
**Goal:** Turn this single-purpose repo into a collection of independent agent/A2A examples. The current project becomes the first example, fully self-contained under `examples/`.

---

## Motivation

The repo currently holds exactly one thing: an A2A agent using Microsoft Agent Framework + Azure AI Foundry, deployable to Azure Functions. The user wants to reuse this repo as a home for multiple, unrelated agent examples going forward, each independently runnable and independently documented.

---

## Architecture

```
agent-examples/                                    (repo root)
├── README.md                                       ← new: repo-level index of examples
├── .gitignore                                      ← stays at root, covers all examples
└── examples/
    └── deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/
        ├── main.py
        ├── function_app.py
        ├── test_client.py
        ├── pyproject.toml
        ├── uv.lock
        ├── requirements.txt
        ├── host.json
        ├── .funcignore
        ├── .env.example
        ├── .python-version
        ├── README.md                               ← existing README, paths unchanged (already self-contained)
        └── docs/superpowers/specs/, docs/superpowers/plans/
            ├── 2026-07-14-a2a-maf-agent-design.md
            ├── 2026-07-14-azure-functions-deploy-design.md
            ├── 2026-07-14-a2a-maf-agent.md
            └── 2026-07-14-azure-functions-deploy.md
```

Each example is fully independent: its own `pyproject.toml`/`uv.lock`, own README, own `docs/`. No shared root-level dependency file. Future examples follow the same pattern — a new folder under `examples/` with its own everything.

---

## Components

**Root `README.md`**
Short intro: this repo is a collection of agent framework / A2A examples. A table listing each example — name, one-line description, link to its folder. Currently one row.

**Example folder:** `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/`
Everything that currently lives at repo root (except root-only files listed below) moves here unchanged, via `git mv` to preserve history. No code changes — only file locations move.

**Root-level `.gitignore`**
Stays at root; patterns (`.venv`, `__pycache__`, `.env`, `local.settings.json`, `.superpowers/`) apply repo-wide regardless of which example folder they occur in.

**Untouched:** `.claude/`, `.superpowers/` — local tooling config/scratch, already gitignored, stay at root.

---

## Data Flow / Process

1. `git mv` each existing file/dir (except `README.md`, `.gitignore`, `.git`, `.claude`, `.superpowers`) into the new example folder.
2. Write a new root `README.md` (example index).
3. Rewrite the example's own `README.md` — content stays the same (setup/run/deploy instructions), since nothing inside the example changes relative to itself.
4. Verify no path references break (e.g. `pyproject.toml`'s `readme = "README.md"` still resolves relative to the example folder — no change needed since it's a relative path).

---

## Testing

- After moving, `cd` into the example folder and run `uv sync` + `uv run main.py` to confirm nothing broke from the move.
- Confirm `git log --follow` on a moved file (e.g. `main.py`) still shows prior history.

---

## Out of Scope

- Adding any new example (this spec only covers restructuring the existing one).
- Renaming the GitHub remote / pushing to GitHub (handled separately once the user provides the remote URL).
- CI/CD.
