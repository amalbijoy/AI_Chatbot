from fastapi import FastAPI, APIRouter, HTTPException
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from pydantic import BaseModel, Field, ConfigDict
from typing import List, Optional
import uuid
from datetime import datetime, timezone
from emergentintegrations.llm.chat import LlmChat, UserMessage

ROOT_DIR = Path(__file__).parent
load_dotenv(ROOT_DIR / '.env')

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Create the main app without a prefix
app = FastAPI()

# Create a router with the /api prefix
api_router = APIRouter(prefix="/api")

# Define Models
class StatusCheck(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_name: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class StatusCheckCreate(BaseModel):
    client_name: str

class ChatMessage(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatSession(BaseModel):
    model_config = ConfigDict(extra="ignore")
    
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    title: str = "New Chat"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=10000)
    session_id: Optional[str] = Field(default=None, min_length=1, max_length=100)

class ChatResponse(BaseModel):
    session_id: str
    user_message: str
    assistant_message: str
    timestamp: datetime

# Add your routes to the router instead of directly to app
@api_router.get("/")
async def root():
    return {"message": "Hello World"}

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.model_dump()
    status_obj = StatusCheck(**status_dict)
    
    # Convert to dict and serialize datetime to ISO string for MongoDB
    doc = status_obj.model_dump()
    doc['timestamp'] = doc['timestamp'].isoformat()
    
    _ = await db.status_checks.insert_one(doc)
    return status_obj

@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    # Exclude MongoDB's _id field from the query results
    status_checks = await db.status_checks.find({}, {"_id": 0}).to_list(1000)
    
    # Convert ISO string timestamps back to datetime objects
    for check in status_checks:
        if isinstance(check['timestamp'], str):
            check['timestamp'] = datetime.fromisoformat(check['timestamp'])
    
    return status_checks

# Chat endpoints
@api_router.post("/chat/sessions", response_model=ChatSession)
async def create_chat_session():
    """Create a new chat session"""
    session = ChatSession()
    doc = session.model_dump()
    doc['created_at'] = doc['created_at'].isoformat()
    doc['updated_at'] = doc['updated_at'].isoformat()
    
    await db.chat_sessions.insert_one(doc)
    return session

@api_router.get("/chat/sessions", response_model=List[ChatSession])
async def get_chat_sessions():
    """Get all chat sessions"""
    sessions = await db.chat_sessions.find({}, {"_id": 0}).sort("updated_at", -1).to_list(1000)
    
    for session in sessions:
        if isinstance(session['created_at'], str):
            session['created_at'] = datetime.fromisoformat(session['created_at'])
        if isinstance(session['updated_at'], str):
            session['updated_at'] = datetime.fromisoformat(session['updated_at'])
    
    return sessions

@api_router.get("/chat/sessions/{session_id}/messages", response_model=List[ChatMessage])
async def get_chat_messages(session_id: str):
    """Get all messages for a session"""
    messages = await db.chat_messages.find(
        {"session_id": session_id},
        {"_id": 0}
    ).sort("timestamp", 1).to_list(1000)
    
    for msg in messages:
        if isinstance(msg['timestamp'], str):
            msg['timestamp'] = datetime.fromisoformat(msg['timestamp'])
    
    return messages

@api_router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """Send a message and get AI response"""
    try:
        # Get or create session
        session_id = request.session_id
        if not session_id:
            session = ChatSession()
            session_doc = session.model_dump()
            session_doc['created_at'] = session_doc['created_at'].isoformat()
            session_doc['updated_at'] = session_doc['updated_at'].isoformat()
            await db.chat_sessions.insert_one(session_doc)
            session_id = session.session_id
        
        # Get API key from environment
        api_key = os.environ.get('EMERGENT_LLM_KEY')
        if not api_key:
            raise HTTPException(status_code=500, detail="API key not configured")
        
        # Get chat history to build context
        history_messages = await db.chat_messages.find(
            {"session_id": session_id},
            {"_id": 0}
        ).sort("timestamp", 1).to_list(1000)
        
        # Build context from history
        context_messages = []
        for msg in history_messages:
            role = "User" if msg['role'] == "user" else "Assistant"
            context_messages.append(f"{role}: {msg['content']}")
        
        # Create full prompt with context
        if context_messages:
            context_text = "\n".join(context_messages[-10:])  # Last 10 messages for context
            full_prompt = f"Previous conversation:\n{context_text}\n\nUser: {request.message}"
        else:
            full_prompt = request.message
        
        # Create LLM chat instance
        chat_instance = LlmChat(
            api_key=api_key,
            session_id=session_id,
            system_message="You are a helpful AI assistant. Provide clear, concise, and friendly responses. Remember the conversation context and refer to previous messages when relevant."
        ).with_model("anthropic", "claude-sonnet-4-5-20250929")
        
        # Send message to Claude
        user_msg = UserMessage(text=full_prompt)
        assistant_response = await chat_instance.send_message(user_msg)
        
        # Save user message
        user_message = ChatMessage(
            session_id=session_id,
            role="user",
            content=request.message
        )
        user_doc = user_message.model_dump()
        user_doc['timestamp'] = user_doc['timestamp'].isoformat()
        await db.chat_messages.insert_one(user_doc)
        
        # Save assistant message
        assistant_message = ChatMessage(
            session_id=session_id,
            role="assistant",
            content=assistant_response
        )
        assistant_doc = assistant_message.model_dump()
        assistant_doc['timestamp'] = assistant_doc['timestamp'].isoformat()
        await db.chat_messages.insert_one(assistant_doc)
        
        # Update session timestamp
        await db.chat_sessions.update_one(
            {"session_id": session_id},
            {"$set": {"updated_at": datetime.now(timezone.utc).isoformat()}}
        )
        
        return ChatResponse(
            session_id=session_id,
            user_message=request.message,
            assistant_message=assistant_response,
            timestamp=datetime.now(timezone.utc)
        )
    
    except HTTPException:
        raise
    except Exception:
        logger.exception("Error in chat endpoint")
        raise HTTPException(status_code=500, detail="Internal server error")

@api_router.delete("/chat/sessions/{session_id}")
async def delete_chat_session(session_id: str):
    """Delete a chat session and its messages"""
    await db.chat_messages.delete_many({"session_id": session_id})
    await db.chat_sessions.delete_one({"session_id": session_id})
    return {"message": "Session deleted successfully"}

# Include the router in the main app
app.include_router(api_router)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=[o.strip() for o in os.environ.get("CORS_ORIGINS", "http://localhost:8501").split(",") if o.strip()],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()