# A2A General Assistant Agent — Design Spec

**Date:** 2026-07-14  
**Project:** `a2a-maf`  
**Stack:** Microsoft Agent Framework + Azure AI Foundry + A2A protocol

---

## Goal

Expose a general-purpose AI assistant as an A2A-compliant HTTP server. Remote agents and clients can discover it via its AgentCard and interact with it using the A2A JSON-RPC protocol.

---

## Architecture

```
main.py
├── FoundryChatClient     — calls Azure AI Foundry chat completions
├── A2AExecutor           — bridges MAF agent ↔ A2A protocol (streaming)
├── DefaultRequestHandler — routes A2A JSON-RPC requests to the executor
├── InMemoryTaskStore     — tracks task state in memory
└── Starlette app
    ├── GET /.well-known/agent.json  — serves AgentCard (agent discovery)
    └── POST /                       — handles A2A JSON-RPC calls
```

Configuration is sourced from environment variables (or a `.env` file):

| Variable | Purpose |
|---|---|
| `FOUNDRY_PROJECT_ENDPOINT` | Azure AI Foundry project endpoint URL |
| `FOUNDRY_MODEL` | Model deployment name |

No config files are committed to the repo.

---

## Components

**`FoundryChatClient`**  
Wraps Azure AI Foundry's chat completions API. Constructed with `project_endpoint` and `model` from env vars. Acts as a MAF-compatible agent via `.as_agent()`.

**`A2AExecutor`**  
Provided by `agent_framework_a2a`. Wraps the MAF agent, manages `AgentSession` creation keyed to the A2A `context_id`, and converts `AgentResponseUpdate` chunks to `TaskArtifactUpdateEvent`s. Runs in streaming mode (`stream=True`).

**`DefaultRequestHandler`**  
Provided by `a2a.server.request_handlers`. Deserializes incoming A2A JSON-RPC messages, manages task lifecycle, and dispatches to `A2AExecutor`.

**`InMemoryTaskStore`**  
Provided by `a2a.server.tasks`. Holds task state in memory — sufficient for a single-process server.

**`AgentCard`**  
Describes the agent for A2A discovery: name, description, capabilities (streaming=True), and the server URL. Served at `GET /.well-known/agent.json`.

**`Starlette app`**  
Lightweight ASGI app. Routes:
- `/.well-known/agent.json` — agent discovery
- `/` — A2A JSON-RPC endpoint (message/send, message/stream, tasks/get, tasks/cancel)

A helper script `test_client.py` sends a test message to the server using `A2AAgent` for manual verification.

---

## Data Flow

1. Client POSTs A2A `message/send` or `message/stream` to `/`
2. `DefaultRequestHandler` deserializes the message, creates/resumes a `Task`
3. `A2AExecutor.execute()` is called with the request context and event queue
4. Executor extracts user text, creates `AgentSession(session_id=context_id)`, calls `agent.run(stream=True)`
5. Foundry streams chat completion chunks as `AgentResponseUpdate`s
6. Executor enqueues `TaskArtifactUpdateEvent`s for each chunk
7. Client receives SSE events (streaming) or final JSON (non-streaming)
8. Task state: `submitted → working → completed` (or `failed` on error)

Session continuity: follow-up messages sharing the same A2A `context_id` reuse the same `AgentSession`, preserving conversation history within a server process lifetime.

---

## Error Handling

- Missing env vars raise on startup (not at request time)
- Agent exceptions are caught by `A2AExecutor` and surface as `TASK_STATE_FAILED` with the error text
- Malformed JSON-RPC requests return HTTP 4xx via `DefaultRequestHandler`

---

## Files to Create

| File | Purpose |
|---|---|
| `main.py` | Starlette app entrypoint (replaces placeholder) |
| `test_client.py` | Manual test script using `A2AAgent` |
| `.env.example` | Documents required env vars |

---

## Out of Scope

- Persistent task store (database)
- Authentication / auth interceptors
- Custom tools / function calling
- Multi-agent orchestration
