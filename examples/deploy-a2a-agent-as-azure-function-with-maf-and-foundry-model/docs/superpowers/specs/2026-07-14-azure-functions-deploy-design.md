# Azure Functions Deployment — Design Spec

**Date:** 2026-07-14  
**Project:** `a2a-maf`  
**Goal:** Deploy the existing Starlette A2A server to Azure Functions using `AsgiMiddleware`, with anonymous auth and no changes to `main.py`.

---

## Architecture

```
function_app.py       ← Azure Functions entry point (new)
├── imports app from main.py
└── wraps with func.AsgiMiddleware — catch-all HTTP trigger, anonymous auth

host.json             ← Functions runtime config (new)
local.settings.json   ← Local dev settings, NOT committed (new, git-ignored)
main.py               ← Unchanged
```

The existing Starlette app (`main.py`) is not modified. `function_app.py` is the sole new code file.

---

## Components

**`function_app.py`**  
Azure Functions Python v2 entry point. Defines one HTTP trigger with:
- Route: `{*route}` (catch-all wildcard)
- Auth level: `ANONYMOUS`
- Handler: `func.AsgiMiddleware(app).handle_async(req, context)`

All A2A paths (`/.well-known/agent-card.json`, `/`) pass through unchanged to Starlette.

**`host.json`**  
Controls the Functions runtime:
- `extensionBundle`: Microsoft Azure Functions Extension Bundle v4 (required for Durable/Storage bindings)
- `extensions.http.routePrefix`: `""` — removes the default `/api/` prefix so A2A routes are served at `/` not `/api/`

**`local.settings.json`** (not committed)  
Local development only:
- `AzureWebJobsStorage`: Azure Storage connection string (or `"UseDevelopmentStorage=true"` with Azurite)
- `FUNCTIONS_WORKER_RUNTIME`: `"python"`
- `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL`: copied from `.env` for local func testing

**Azure Application Settings** (set in portal or via `az functionapp config appsettings set`)  
- `FOUNDRY_PROJECT_ENDPOINT`
- `FOUNDRY_MODEL`
- `AZURE_CLIENT_ID` (if using user-assigned managed identity)

**Managed Identity**  
`DefaultAzureCredential` resolves automatically in Azure via the Function App's system-assigned or user-assigned managed identity. The managed identity must have the **Azure AI Developer** role on the Foundry project.

---

## Data Flow

1. Caller POSTs to `https://<funcapp>.azurewebsites.net/` (A2A JSON-RPC)
2. Azure Functions runtime receives request → catch-all trigger in `function_app.py`
3. `func.AsgiMiddleware(app)` translates `HttpRequest` → ASGI scope → Starlette
4. Starlette routes to `DefaultRequestHandler` → `A2AExecutor` → `FoundryChatClient` → Azure AI Foundry
5. Response flows back through ASGI middleware → Functions runtime → caller

AgentCard discovery: `GET https://<funcapp>.azurewebsites.net/.well-known/agent-card.json`

---

## AgentCard URL

The `SERVER_URL` in `main.py` is built from `HOST` and `PORT` env vars (defaults: `localhost:9999`). In Azure, these must be overridden via Application Settings:
- `HOST`: `<funcapp>.azurewebsites.net`
- `PORT`: `443`

This ensures the AgentCard's `supported_interfaces[0].url` points to the correct public URL.

---

## Deployment

```bash
func azure functionapp publish <function-app-name> --python
```

Prerequisites:
- Azure Functions Core Tools v4 installed (`npm install -g azure-functions-core-tools@4`)
- Logged in: `az login`
- Function App already provisioned in Azure

---

## Files to Create/Modify

| File | Action | Purpose |
|---|---|---|
| `function_app.py` | Create | Azure Functions entry point with AsgiMiddleware |
| `host.json` | Create | Runtime config — removes `/api/` prefix |
| `local.settings.json` | Create | Local dev config — git-ignored |
| `.gitignore` | Modify | Add `local.settings.json` |
| `pyproject.toml` | Modify | Add `azure-functions` dependency |

`main.py`, `test_client.py` — **no changes**.

---

## Out of Scope

- Provisioning the Function App (already exists)
- CI/CD pipeline
- Custom domain / TLS certificates
- Authentication / access control beyond anonymous
- Streaming SSE responses (Azure Functions HTTP trigger buffers responses — streaming may not work end-to-end; non-streaming A2A calls will work correctly)
