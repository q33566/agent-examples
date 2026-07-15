# A2A General Assistant Agent Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Expose a `FoundryChatClient`-powered general assistant as an A2A-compliant HTTP server using Microsoft Agent Framework.

**Architecture:** A single Starlette app wires together `FoundryChatClient` → `A2AExecutor` → `DefaultRequestHandler` → ASGI routes. Configuration is read from environment variables (loaded from `.env`). A companion `test_client.py` script exercises the running server end-to-end.

**Tech Stack:** Python 3.13, `agent-framework`, `agent-framework-foundry`, `agent-framework-a2a`, `a2a` SDK, `starlette`, `uvicorn`, `azure-identity`, `python-dotenv`

## Global Constraints

- Python `>=3.13`
- Use `.venv` (already created via `uv`); install new deps with `uv add <pkg>`
- All config via env vars — never hardcode credentials or endpoints
- `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL` must be set before running
- Streaming enabled on the A2A server (`stream=True` in `A2AExecutor`)
- Server default port: `9999`

---

### Task 1: Add missing dependencies and `.env.example`

**Files:**
- Modify: `pyproject.toml`
- Create: `.env.example`

**Interfaces:**
- Produces: working `uv sync` with `uvicorn`, `azure-identity`, `python-dotenv`, `starlette` available

- [ ] **Step 1: Add dependencies**

Run:
```
uv add uvicorn azure-identity python-dotenv starlette
```

Expected: `pyproject.toml` updated, `.venv` synced with no errors.

- [ ] **Step 2: Verify packages are importable**

Run:
```
.venv\Scripts\python.exe -c "import uvicorn, azure.identity, dotenv, starlette; print('OK')"
```

Expected output: `OK`

- [ ] **Step 3: Create `.env.example`**

Create file `.env.example` with this exact content:

```
# Azure AI Foundry project endpoint
# e.g. https://your-project.services.ai.azure.com
FOUNDRY_PROJECT_ENDPOINT=

# Model deployment name
# e.g. gpt-4o
FOUNDRY_MODEL=

# Server host and port (optional, defaults shown)
HOST=localhost
PORT=9999
```

- [ ] **Step 4: Commit**

```
git add pyproject.toml uv.lock .env.example
git commit -m "chore: add runtime dependencies and .env.example"
```

---

### Task 2: Build and verify the Starlette A2A server (`main.py`)

**Files:**
- Modify: `main.py` (replace placeholder)

**Interfaces:**
- Consumes:
  - `FoundryChatClient(credential=..., env_file_path=".env")` → `.as_agent(name=..., instructions=...)`
  - `A2AExecutor(agent, stream=True)` from `agent_framework_a2a`
  - `DefaultRequestHandler(agent_executor=..., task_store=..., agent_card=...)` from `a2a.server.request_handlers`
  - `InMemoryTaskStore()` from `a2a.server.tasks`
  - `AgentCard`, `AgentCapabilities`, `AgentInterface` from `a2a.types`
  - `create_agent_card_routes`, `create_jsonrpc_routes` from `a2a.server.routes`
  - `Starlette` from `starlette.applications`
  - `uvicorn.run` for entrypoint
- Produces: `app` (Starlette ASGI app), `main()` entrypoint

- [ ] **Step 1: Replace `main.py` with the server implementation**

Write `main.py` with this exact content:

```python
import os

import uvicorn
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.routes import create_agent_card_routes, create_jsonrpc_routes
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCapabilities, AgentCard, AgentInterface
from agent_framework_a2a import A2AExecutor
from agent_framework_foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from starlette.applications import Starlette

load_dotenv()

HOST = os.getenv("HOST", "localhost")
PORT = int(os.getenv("PORT", "9999"))
SERVER_URL = f"http://{HOST}:{PORT}/"

agent_card = AgentCard(
    name="General Assistant",
    description="A general-purpose AI assistant powered by Azure AI Foundry.",
    version="1.0.0",
    default_input_modes=["text"],
    default_output_modes=["text"],
    capabilities=AgentCapabilities(streaming=True),
    supported_interfaces=[
        AgentInterface(url=SERVER_URL, protocol_binding="JSONRPC"),
    ],
    skills=[],
)

_client = FoundryChatClient(credential=DefaultAzureCredential())
_agent = _client.as_agent(
    name="General Assistant",
    instructions="You are a helpful general-purpose AI assistant.",
)

_request_handler = DefaultRequestHandler(
    agent_executor=A2AExecutor(_agent, stream=True),
    task_store=InMemoryTaskStore(),
    agent_card=agent_card,
)

app = Starlette(
    routes=[
        *create_agent_card_routes(agent_card),
        *create_jsonrpc_routes(_request_handler, "/"),
    ],
)


def main() -> None:
    uvicorn.run(app, host=HOST, port=PORT)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify the module loads without errors (env vars must be set)**

Run:
```
.venv\Scripts\python.exe -c "from main import app; print('app loaded OK')"
```

Expected output: `app loaded OK`

If you see a `ValueError` about missing env vars, confirm `.env` is present and populated with `FOUNDRY_PROJECT_ENDPOINT` and `FOUNDRY_MODEL`.

- [ ] **Step 3: Start the server**

Run (in a separate terminal or background):
```
.venv\Scripts\python.exe main.py
```

Expected: Server starts, logs show `Uvicorn running on http://localhost:9999`

- [ ] **Step 4: Verify the AgentCard endpoint**

Run:
```
.venv\Scripts\python.exe -c "import urllib.request, json; r=urllib.request.urlopen('http://localhost:9999/.well-known/agent.json'); print(json.dumps(json.load(r), indent=2))"
```

Expected: JSON with `"name": "General Assistant"` and `"streaming": true` in capabilities.

- [ ] **Step 5: Commit**

```
git add main.py
git commit -m "feat: add A2A server with FoundryChatClient and Starlette"
```

---

### Task 3: Build the manual test client (`test_client.py`)

**Files:**
- Create: `test_client.py`

**Interfaces:**
- Consumes: running server at `http://localhost:9999/` (from Task 2)
- Consumes: `A2AAgent(url=...)` from `agent_framework_a2a`
- Consumes: `AgentSession` from `agent_framework`

- [ ] **Step 1: Create `test_client.py`**

Write `test_client.py` with this exact content:

```python
"""Manual test script — run with the server already started on port 9999."""

import asyncio

from agent_framework import AgentSession
from agent_framework_a2a import A2AAgent


async def main() -> None:
    server_url = "http://localhost:9999/"

    async with A2AAgent(url=server_url, name="General Assistant") as agent:
        session = AgentSession()

        # First turn
        print("--- Turn 1 ---")
        response = await agent.run("What is the capital of France?", session=session)
        for msg in response.messages:
            for content in msg.contents:
                if content.type == "text":
                    print(f"Agent: {content.text}")

        # Second turn (same session — tests context continuity)
        print("\n--- Turn 2 ---")
        response = await agent.run("And what is its most famous landmark?", session=session)
        for msg in response.messages:
            for content in msg.contents:
                if content.type == "text":
                    print(f"Agent: {content.text}")


if __name__ == "__main__":
    asyncio.run(main())
```

- [ ] **Step 2: Run the test client (server must be running)**

Run:
```
.venv\Scripts\python.exe test_client.py
```

Expected: Two agent responses printed, Turn 2 answer references Paris/Eiffel Tower (demonstrating context continuity within the session).

- [ ] **Step 3: Commit**

```
git add test_client.py
git commit -m "feat: add manual A2A test client"
```
