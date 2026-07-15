# Restructure Repo as Multi-Example Collection Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Move the existing single A2A/Foundry/Azure-Functions project into `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/`, and replace the root `README.md` with a repo-level index, so the repo becomes a home for multiple independent agent examples.

**Architecture:** Pure file relocation via `git mv` (no code changes) plus one new root `README.md`. Everything currently at repo root except `README.md`, `.gitignore`, `.git`, `.claude`, `.superpowers`, and the two meta spec/plan docs about this restructuring itself moves into the new example folder, carrying its own `docs/superpowers/{specs,plans}` with it.

**Tech Stack:** git, uv (Python package manager), bash.

## Global Constraints

- Preserve git history for every moved file — use `git mv`, never delete+recreate.
- No content/code changes to any moved file in this plan — only paths change.
- The example folder name is exactly: `deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model`.
- The two design docs dated 2026-07-14 (`a2a-maf-agent-design.md`, `azure-functions-deploy-design.md`) and their matching plans (`a2a-maf-agent.md`, `azure-functions-deploy.md`) belong to the example and move with it.
- The 2026-07-15 restructuring spec (`2026-07-15-restructure-as-examples-repo-design.md`) and this plan file describe the whole repo, not the example — they stay at root under `docs/superpowers/`.

---

### Task 1: Move example files into `examples/` folder

**Files:**
- Move: `.env.example` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/.env.example`
- Move: `.funcignore` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/.funcignore`
- Move: `.python-version` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/.python-version`
- Move: `function_app.py` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/function_app.py`
- Move: `host.json` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/host.json`
- Move: `main.py` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/main.py`
- Move: `pyproject.toml` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/pyproject.toml`
- Move: `requirements.txt` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/requirements.txt`
- Move: `test_client.py` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/test_client.py`
- Move: `uv.lock` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/uv.lock`
- Move: `README.md` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/README.md` (temporary location — Task 2 writes a fresh root `README.md`)
- Move: `docs/superpowers/specs/2026-07-14-a2a-maf-agent-design.md` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/docs/superpowers/specs/2026-07-14-a2a-maf-agent-design.md`
- Move: `docs/superpowers/specs/2026-07-14-azure-functions-deploy-design.md` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/docs/superpowers/specs/2026-07-14-azure-functions-deploy-design.md`
- Move: `docs/superpowers/plans/2026-07-14-a2a-maf-agent.md` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/docs/superpowers/plans/2026-07-14-a2a-maf-agent.md`
- Move: `docs/superpowers/plans/2026-07-14-azure-functions-deploy.md` → `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/docs/superpowers/plans/2026-07-14-azure-functions-deploy.md`

**Interfaces:**
- Consumes: nothing (first task).
- Produces: the example folder `examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/` containing every file listed above, for Task 2 (root README) and Task 3 (verification) to build on.

- [ ] **Step 1: Create the example directory tree**

```bash
mkdir -p "examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/docs/superpowers/specs"
mkdir -p "examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/docs/superpowers/plans"
```

- [ ] **Step 2: Move top-level project files with `git mv`**

```bash
EX="examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model"
git mv .env.example "$EX/.env.example"
git mv .funcignore "$EX/.funcignore"
git mv .python-version "$EX/.python-version"
git mv function_app.py "$EX/function_app.py"
git mv host.json "$EX/host.json"
git mv main.py "$EX/main.py"
git mv pyproject.toml "$EX/pyproject.toml"
git mv requirements.txt "$EX/requirements.txt"
git mv test_client.py "$EX/test_client.py"
git mv uv.lock "$EX/uv.lock"
git mv README.md "$EX/README.md"
```

- [ ] **Step 3: Move the example's own design docs with `git mv`**

```bash
EX="examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model"
git mv docs/superpowers/specs/2026-07-14-a2a-maf-agent-design.md "$EX/docs/superpowers/specs/2026-07-14-a2a-maf-agent-design.md"
git mv docs/superpowers/specs/2026-07-14-azure-functions-deploy-design.md "$EX/docs/superpowers/specs/2026-07-14-azure-functions-deploy-design.md"
git mv docs/superpowers/plans/2026-07-14-a2a-maf-agent.md "$EX/docs/superpowers/plans/2026-07-14-a2a-maf-agent.md"
git mv docs/superpowers/plans/2026-07-14-azure-functions-deploy.md "$EX/docs/superpowers/plans/2026-07-14-azure-functions-deploy.md"
```

- [ ] **Step 4: Verify git status shows renames, not add+delete**

Run: `git status`
Expected: all entries under "Changes to be committed" show `renamed:` (git detects `git mv` as a rename since content is unchanged).

- [ ] **Step 5: Verify history is preserved on a moved file**

Run: `git log --follow --oneline "examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/main.py"`
Expected: shows the pre-move commit history of `main.py` (e.g. commits like "feat: add Azure Functions entry point...", "fix: declare missing agent-framework-a2a...").

---

### Task 2: Write new root README.md as example index

**Files:**
- Create: `README.md` (repo root — Task 1 moved the old one away, so root is currently empty of a README)

**Interfaces:**
- Consumes: the example folder name from Task 1: `deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model`.
- Produces: root `README.md`, the entry point anyone lands on when opening the repo on GitHub.

- [ ] **Step 1: Write the root README**

Create `README.md` with this exact content:

```markdown
# agent-examples

A collection of standalone examples for building and deploying AI agents — using frameworks like the Microsoft Agent Framework, the A2A (Agent-to-Agent) protocol, and various model providers and deployment targets.

Each example under `examples/` is fully self-contained: its own dependencies, its own README, its own setup instructions. Pick the one you need and follow its README.

## Examples

| Example | Description |
|---|---|
| [`deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model`](examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/) | A general-purpose assistant built with the Microsoft Agent Framework and an Azure AI Foundry model, exposed over the A2A protocol, deployable to Azure Functions. |
```

- [ ] **Step 2: Verify the link resolves**

Run: `ls "examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/README.md"`
Expected: file exists (confirms the relative link in the table is valid).

- [ ] **Step 3: Stage the new root README**

```bash
git add README.md
```

---

### Task 3: Verify the moved example still runs

**Files:**
- None created or modified — verification only, run from inside the example folder.

**Interfaces:**
- Consumes: the fully-populated example folder from Task 1.
- Produces: confidence that the move introduced no breakage, before committing.

- [ ] **Step 1: Sync dependencies from the new location**

```bash
cd "examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model"
uv sync
```

Expected: completes without error (resolves the same lockfile as before — `pyproject.toml`'s `readme = "README.md"` is a relative path and still resolves correctly next to it).

- [ ] **Step 2: Confirm the app imports cleanly**

```bash
uv run python -c "from main import app; print(app)"
```

Expected: prints a Starlette application repr, no import errors (confirms no code referenced the old root-relative paths).

- [ ] **Step 3: Return to repo root**

```bash
cd ../..
```

---

### Task 4: Commit the restructuring

**Files:**
- All files moved in Task 1, plus `README.md` from Task 2.

**Interfaces:**
- Consumes: staged renames from Task 1 and the new README from Task 2.
- Produces: a single commit capturing the full restructuring.

- [ ] **Step 1: Stage everything**

```bash
git add -A
git status
```

Expected: only renames (`examples/...`) and one new file (`README.md`) are staged — no unrelated changes.

- [ ] **Step 2: Commit**

```bash
git commit -m "$(cat <<'EOF'
refactor: restructure repo as multi-example collection

Move the existing A2A/Foundry/Azure Functions project into
examples/deploy-a2a-agent-as-azure-function-with-maf-and-foundry-model/
and add a root README indexing all examples, so the repo can hold
multiple independent agent examples going forward.

Co-Authored-By: Claude Sonnet 5 <noreply@anthropic.com>
EOF
)"
```

- [ ] **Step 3: Verify clean working tree**

Run: `git status`
Expected: `nothing to commit, working tree clean`
