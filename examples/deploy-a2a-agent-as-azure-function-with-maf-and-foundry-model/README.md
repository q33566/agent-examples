# a2a-maf

A general-purpose AI assistant agent built on the [Microsoft Agent Framework](https://github.com/microsoft/agent-framework) and [Azure AI Foundry](https://azure.microsoft.com/products/ai-foundry), exposed over the [A2A (Agent-to-Agent) protocol](https://github.com/a2aproject/A2A). Runs standalone via `uvicorn`/Starlette or deployed to Azure Functions.

## Architecture

- `main.py` — Starlette app. Builds an `AgentCard`, wires a `FoundryChatClient` agent through `A2AExecutor`, and serves A2A JSON-RPC routes plus agent-card discovery (`/.well-known/agent-card.json`).
- `function_app.py` — Azure Functions entry point. Wraps the same Starlette `app` from `main.py` with `func.AsgiMiddleware` behind a catch-all HTTP trigger (anonymous auth), so the app runs unchanged on Functions.
- `test_client.py` — Manual multi-turn test script using `A2AAgent` against a running server.
- Auth to Azure AI Foundry uses `DefaultAzureCredential` (local dev credentials, or the Function App's managed identity in Azure — requires the **Azure AI Developer** role on the Foundry project).

## Requirements

- Python >= 3.13
- An Azure AI Foundry project with a deployed model

## Setup

```bash
uv sync
cp .env.example .env
```

Fill in `.env`:

| Variable | Description |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint, e.g. `https://your-project.services.ai.azure.com` |
| `FOUNDRY_MODEL` | Model deployment name, e.g. `gpt-4o` |
| `HOST` | Server host (default `localhost`) |
| `PORT` | Server port (default `9999`) |

## Run locally

```bash
uv run main.py
```

Or test with the manual client (adjust `SERVER_URL` to match, e.g. `http://localhost:9999/`):

```bash
uv run test_client.py
```

## Deploy to Azure Functions

```bash
func azure functionapp publish <function-app-name> --python
```

Prerequisites: Azure Functions Core Tools v4, `az login`, and a Function App already provisioned. Set `FOUNDRY_PROJECT_ENDPOINT`, `FOUNDRY_MODEL`, `HOST` (`<funcapp>.azurewebsites.net`), and `PORT` (`443`) as Application Settings so the AgentCard advertises the correct public URL.

Note: Azure Functions HTTP triggers buffer responses, so streaming (SSE) A2A calls may not work end-to-end; non-streaming calls work correctly.

See `docs/superpowers/specs/` for detailed design notes on the agent and the Functions deployment.
