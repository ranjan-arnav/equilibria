from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List
from backend.models import HealthState, ChatMessage
from backend.store import BackendStore
from src.agents.chat_agent import ConversationalAgent

router = APIRouter()

# Wrapper to use existing agent logic with store
agent = ConversationalAgent()

class ChatRequest(BaseModel):
    message: str
    context: Optional[HealthState] = None

class ChatResponse(BaseModel):
    response: str
    history: List[ChatMessage]

@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        store = BackendStore()
        
        # 1. Save User Message
        store.add_chat_message(role="user", content=request.message)
        
        # 2. Get Agent Response
        # Update context first if provided
        if request.context:
            agent.update_context(state=request.context)
            
        response_text = agent.chat(request.message)
        
        # 3. Save Assistant Message
        store.add_chat_message(role="assistant", content=response_text)
        
        # 4. Return response with full history
        # Convert dicts to Pydantic models
        history_objs = [ChatMessage(**msg) for msg in store.get_chat_history()]
        
        return ChatResponse(
            response=response_text,
            history=history_objs
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
