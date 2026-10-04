# AI Chatbot

> Full-stack learning/prototype application combining FastAPI, Streamlit, MongoDB, and Anthropic Claude Sonnet 4.5.

## Overview

The application provides multi-turn chat sessions with persistent message history.

The current implementation uses the model identifier:

```text
anthropic / claude-sonnet-4-5-20250929
```

The model is accessed through the `emergentintegrations` library.

## Features

- Create, list, and delete chat sessions
- Persist sessions and messages in MongoDB
- Multi-turn context handling
- Streamlit chat interface
- FastAPI backend
- JSON API for chat operations
- Input-size validation for chat requests
- Explicit CORS configuration through an environment variable

## Architecture

```text
Streamlit
    │
    ▼
FastAPI
    │
    ├── MongoDB
    │     ├── chat_sessions
    │     └── chat_messages
    │
    └── emergentintegrations
            │
            ▼
        Claude Sonnet 4.5
```

For chat requests, the backend loads recent stored messages for the selected session and includes the latest context in the model prompt. Session records and message records are then persisted back to MongoDB.

## Requirements

- Python 3.9+
- MongoDB reachable from the backend
- Internet access for the model API and, when applicable, dependency installation

## Setup

### 1. Backend

```bash
cd backend
python -m pip install -r requirements.txt
```

Create a local `backend/.env` file from the example:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=http://localhost:8501
EMERGENT_LLM_KEY=YOUR_EMERGENT_LLM_KEY
```

Start FastAPI:

```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The API will be available at `http://localhost:8001`.

### 2. Streamlit frontend

From the repository root:

```bash
python -m pip install -r requirements_streamlit.txt
streamlit run streamlit_app.py --server.port 8501
```

The UI will be available at `http://localhost:8501`.

## API

All application routes are under `/api`.

| Method | Endpoint | Purpose |
|---|---|---|
| GET | `/api/` | Health-style root response |
| POST | `/api/chat/sessions` | Create a chat session |
| GET | `/api/chat/sessions` | List sessions |
| GET | `/api/chat/sessions/{session_id}/messages` | List messages for a session |
| POST | `/api/chat` | Send a message and receive an AI response |
| DELETE | `/api/chat/sessions/{session_id}` | Delete a session and its messages |

Example:

```bash
curl -X POST http://localhost:8001/api/chat   -H "Content-Type: application/json"   -d '{"message":"Hello!","session_id":"your-session-id"}'
```

## Security and scope

This is a **learning/prototype application**, not a hardened multi-tenant service.

Current security-related behavior includes:

- API credentials are loaded from environment variables
- Real secrets are excluded from the current source tree
- CORS defaults to the local Streamlit origin and can be overridden explicitly
- Chat input length is bounded
- Unexpected backend failures are logged while the API returns a generic error

Important limitations remain:

- There is no user authentication or authorization
- Chat sessions are not bound to a user identity
- There is no application-level rate limiting
- The database connection is configured for the deployment environment rather than secured by this repository
- A credential that was previously committed to Git history must still be considered compromised until it is rotated and historical exposure is removed

See [SECURITY.md](SECURITY.md) for the security checklist.

## Testing

The repository includes a GitHub Actions workflow that performs Python compilation and checks the current tree for the previously exposed credential pattern.

Manual API verification can be performed with `curl` against the running backend.

This repository does not currently claim a comprehensive end-to-end integration test suite.

## Project structure

```text
AI_Chatbot/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env.example
├── streamlit_app.py
├── requirements_streamlit.txt
├── SECURITY.md
├── LICENSE
└── README.md
```

The local `backend/.env` file is configuration, not source-controlled project content.

## License

See [LICENSE](LICENSE).
