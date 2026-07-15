# Azure Functions Deployment Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Wrap the existing Starlette A2A server with `func.AsgiMiddleware` so it runs on Azure Functions with anonymous auth and no route prefix.

**Architecture:** A new `function_app.py` imports the Starlette `app` from `main.py` and registers a single catch-all HTTP trigger using `func.AsgiMiddleware`. `host.json` removes the default `/api/` route prefix. `local.settings.json` holds local dev config and is git-ignored.

**Tech Stack:** Python 3.13, `azure-functions`, `func.AsgiMiddleware`, Azure Functions Core Tools v4, Azure Functions Python v2 programming model.

## Global Constraints

- Python `>=3.13`; use `.venv` (managed by `uv`); install new deps with `uv add <pkg>`
- Azure Functions **Python v2 programming model** — decorators on `app = func.FunctionApp()`
- Auth level: `func.AuthLevel.ANONYMOUS` on all triggers
- Route prefix: `""` (empty) in `host.json` — removes the default `/api/` prefix
- `local.settings.json` must NOT be committed — add to `.gitignore`
- `main.py` must NOT be modified
- `SERVER_URL` in `main.py` reads `HOST` and `PORT` from env — set `HOST=<funcapp>.azurewebsites.net` and `PORT=443` as Azure Application Settings before deploying

---

### Task 1: Add `azure-functions` dependency and config files

**Files:**
- Modify: `pyproject.toml`
- Modify: `.gitignore`
- Create: `host.json`
- Create: `local.settings.json`

**Interfaces:**
- Produces: `host.json` with `routePrefix: ""` consumed by Task 2 verification; `local.settings.json` for local func testing

- [ ] **Step 1: Add `azure-functions` dependency**

Run:
```
uv add azure-functions
```

Expected: `pyproject.toml` updated, `.venv` synced with no errors.

- [ ] **Step 2: Verify `azure-functions` is importable**

Run:
```
.venv\Scripts\python.exe -c "import azure.functions as func; print(func.__version__)"
```

Expected: a version string like `1.21.3` (no import error).

- [ ] **Step 3: Add `local.settings.json` to `.gitignore`**

Edit `.gitignore` — append to the "Environment files" section:

```
# Environment files
.env
local.settings.json
```

- [ ] **Step 4: Create `host.json`**

Create file `host.json` with this exact content:

```json
{
  "version": "2.0",
  "extensionBundle": {
    "id": "Microsoft.Azure.Functions.ExtensionBundle",
    "version": "[4.*, 5.0.0)"
  },
  "extensions": {
    "http": {
      "routePrefix": ""
    }
  }
}
```

- [ ] **Step 5: Create `local.settings.json`**

Create file `local.settings.json` with this exact content (fill in real values from your `.env`):

```json
{
  "IsEncrypted": false,
  "Values": {
    "AzureWebJobsStorage": "UseDevelopmentStorage=true",
    "FUNCTIONS_WORKER_RUNTIME": "python",
    "FOUNDRY_PROJECT_ENDPOINT": "<paste from .env>",
    "FOUNDRY_MODEL": "<paste from .env>",
    "HOST": "localhost",
    "PORT": "7071"
  }
}
```

Note: `AzureWebJobsStorage: "UseDevelopmentStorage=true"` requires Azurite running locally. Alternatively set it to a real Azure Storage connection string.

- [ ] **Step 6: Verify `local.settings.json` is git-ignored**

Run:
```
git status
```

Expected: `local.settings.json` does NOT appear in the output (it is ignored). `host.json` DOES appear as untracked.

- [ ] **Step 7: Commit**

```
git add pyproject.toml uv.lock .gitignore host.json
git commit -m "chore: add azure-functions dependency and Functions config files"
```

---

### Task 2: Create `function_app.py` and verify locally

**Files:**
- Create: `function_app.py`

**Interfaces:**
- Consumes: `app` (Starlette ASGI app) from `main.py` — `from main import app`
- Consumes: `host.json` with `routePrefix: ""`
- Produces: Azure Functions entry point importable as `function_app` — the Functions host discovers it automatically

- [ ] **Step 1: Create `function_app.py`**

Create file `function_app.py` with this exact content:

```python
import azure.functions as func

from main import app

_func_app = func.FunctionApp(http_auth_level=func.AuthLevel.ANONYMOUS)


@_func_app.route(route="{*route}", methods=["GET", "POST", "PUT", "DELETE", "PATCH", "OPTIONS", "HEAD"])
async def a2a_handler(req: func.HttpRequest, context: func.Context) -> func.HttpResponse:
    return await func.AsgiMiddleware(app).handle_async(req, context)
```

- [ ] **Step 2: Verify the module loads without errors**

Run:
```
.venv\Scripts\python.exe -c "from function_app import _func_app; print('function_app loaded OK')"
```

Expected output: `function_app loaded OK`

- [ ] **Step 3: Start the Functions host locally**

Prerequisite: Azure Functions Core Tools v4 must be installed. Verify:
```
func --version
```
Expected: `4.x.x`

If not installed, run: `npm install -g azure-functions-core-tools@4 --unsafe-perm true`

Start the host:
```
func start
```

Expected: Functions host starts, output includes:
```
Functions:
        a2a_handler: [GET,POST,...] http://localhost:7071/{*route}
```

- [ ] **Step 4: Test the AgentCard endpoint locally**

In a second terminal (Functions host must be running):
```
.venv\Scripts\python.exe -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:7071/.well-known/agent-card.json'); print(json.dumps(json.load(r), indent=2))"
```

Expected: JSON with `"name": "General Assistant"` and `"streaming": true`.

Note: The AgentCard `url` field will show `http://localhost:7071/` because `HOST=localhost` and `PORT=7071` in `local.settings.json`. This is correct for local testing.

Stop the Functions host after verification (Ctrl+C).

- [ ] **Step 5: Commit**

```
git add function_app.py
git commit -m "feat: add Azure Functions entry point with AsgiMiddleware"
```

---

### Task 3: Deploy to Azure and verify

**Files:**
- No new files — deployment only

**Interfaces:**
- Consumes: `function_app.py`, `host.json`, `pyproject.toml` from Tasks 1–2
- Consumes: existing Azure Function App (already provisioned)

- [ ] **Step 1: Confirm you are logged in to Azure**

Run:
```
az account show
```

Expected: JSON showing your subscription. If not logged in, run `az login` first.

- [ ] **Step 2: Set required Application Settings on the Function App**

Replace `<function-app-name>` with your actual Function App name, and fill in real values:

```
az functionapp config appsettings set --name <function-app-name> --resource-group <resource-group> --settings FOUNDRY_PROJECT_ENDPOINT="<your-endpoint>" FOUNDRY_MODEL="<your-model>" HOST="<function-app-name>.azurewebsites.net" PORT="443"
```

Expected: JSON listing all app settings including the four you just set.

- [ ] **Step 3: Deploy with Azure Functions Core Tools**

Run from the project root:
```
func azure functionapp publish <function-app-name> --python
```

Expected: Upload completes, output ends with:
```
Deployment successful.
Remote build succeeded!
```

- [ ] **Step 4: Verify the AgentCard endpoint in Azure**

Replace `<function-app-name>` with your actual name:
```
.venv\Scripts\python.exe -c "import urllib.request, json; r=urllib.request.urlopen('https://<function-app-name>.azurewebsites.net/.well-known/agent-card.json'); print(json.dumps(json.load(r), indent=2))"
```

Expected: JSON with `"name": "General Assistant"` and the `url` in `supported_interfaces` pointing to `https://<function-app-name>.azurewebsites.net/`.

- [ ] **Step 5: Send a test A2A message**

Edit `test_client.py` temporarily (or run inline) to point at the Azure URL:

```
.venv\Scripts\python.exe -c "
import asyncio
from agent_framework import AgentSession
from agent_framework_a2a import A2AAgent

async def main():
    async with A2AAgent(url='https://<function-app-name>.azurewebsites.net/', name='General Assistant') as agent:
        session = AgentSession()
        response = await agent.run('What is the capital of France?', session=session)
        for msg in response.messages:
            for content in msg.contents:
                if content.type == 'text':
                    print(f'Agent: {content.text}')

asyncio.run(main())
"
```

Expected: Agent responds mentioning Paris.

- [ ] **Step 6: Commit deployment artifacts**

```
git add pyproject.toml uv.lock
git commit -m "chore: record deployment to Azure Functions"
```
