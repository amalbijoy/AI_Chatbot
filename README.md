# AI Chatbot Application

A full-stack AI chatbot application powered by Claude Sonnet 4.5, built with FastAPI, Streamlit, and MongoDB.

## Features

- Real-time AI conversations using Claude Sonnet 4.5
- Multi-turn conversation with context memory
- Chat history persistence in MongoDB
- Multiple chat session management
- Streamlit-based chat interface
- RESTful API with FastAPI

## System Architecture

### Backend — FastAPI
- RESTful API endpoints for chat operations
- MongoDB integration for persistence
- Claude Sonnet 4.5 integration through the `emergentintegrations` library
- Async operations for API handling

### Frontend — Streamlit
- Interactive chat interface
- Session management sidebar
- Real-time message display
- Chat history navigation

### Database — MongoDB
- `chat_sessions`: Stores chat session metadata
- `chat_messages`: Stores messages associated with sessions

## Technology Stack

- **Backend:** FastAPI, Python 3.9+
- **Frontend:** Streamlit
- **Database:** MongoDB
- **AI Model:** Claude Sonnet 4.5
- **LLM Integration:** `emergentintegrations`

## Installation & Setup

### Prerequisites

- Python 3.9+
- MongoDB running on localhost:27017
- Internet connection for model API calls

### Backend Setup

1. Navigate to the backend directory:
```bash
cd backend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables in `backend/.env`:

```env
MONGO_URL=mongodb://localhost:27017
DB_NAME=test_database
CORS_ORIGINS=*
EMERGENT_LLM_KEY=YOUR_EMERGENT_LLM_KEY
```

> **Security:** Never commit real API keys or other credentials to Git. Store secrets only in your local `.env` file or a proper secrets manager.

4. Start the FastAPI server:
```bash
uvicorn server:app --host 0.0.0.0 --port 8001 --reload
```

The backend API will be available at `http://localhost:8001`.

### Streamlit Frontend Setup

1. Install Streamlit dependencies:
```bash
pip install -r requirements_streamlit.txt
```

2. Set the backend URL:
```bash
export BACKEND_URL=http://localhost:8001
```

3. Run the Streamlit app:
```bash
streamlit run streamlit_app.py --server.port 8501
```

The Streamlit UI will be available at `http://localhost:8501`.

## API Endpoints

### Chat Endpoints

- `POST /api/chat/sessions` — Create a new chat session
- `GET /api/chat/sessions` — Get all chat sessions
- `GET /api/chat/sessions/{session_id}/messages` — Get messages for a session
- `POST /api/chat` — Send a message and get an AI response
- `DELETE /api/chat/sessions/{session_id}` — Delete a chat session

### Example API Usage

```bash
# Create a new session
curl -X POST http://localhost:8001/api/chat/sessions

# Send a message
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello, how are you?","session_id":"your-session-id"}'
```

## Usage

1. Start the backend server.
2. Start the Streamlit frontend.
3. Open `http://localhost:8501`.
4. Click **New Chat** to start a conversation.
5. Type a message and press Enter.
6. The AI responds using Claude Sonnet 4.5.
7. Switch between chats using the sidebar.

## Project Structure

```text
AI_Chatbot/
├── backend/
│   ├── server.py
│   ├── requirements.txt
│   └── .env
├── streamlit_app.py
├── requirements_streamlit.txt
└── README.md
```

## Design Decisions

1. **FastAPI** — provides async support and automatic API documentation.
2. **Streamlit** — keeps the frontend simple and fast to iterate on.
3. **MongoDB** — provides flexible persistence for sessions and messages.
4. **Claude Sonnet 4.5** — provides the conversational model used by the application.
5. **Session-based architecture** — keeps independent conversations isolated from one another.
6. **LLM integration layer** — keeps model-provider access behind a reusable integration library.

## Testing

Test the backend API with:

```bash
curl http://localhost:8001/api/
```

Or create a test session and send a message:

```bash
curl -X POST http://localhost:8001/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"Hello!"}'
```

## Troubleshooting

- **MongoDB connection error:** Ensure MongoDB is running on localhost:27017.
- **API key error:** Set `EMERGENT_LLM_KEY` in `backend/.env` using your own key.
- **CORS issues:** Configure `CORS_ORIGINS` appropriately for your environment.
- **Port already in use:** Change ports if 8001 or 8501 are occupied.

## License

MIT License
