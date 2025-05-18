from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from openai_summarize import LocalSummarize
import logging

router = APIRouter(tags=["chatbot"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("chatbot")

class ChatMessage(BaseModel):
    role: str  
    content: str

class ChatRequest(BaseModel):
    prompt: str
    history: Optional[List[ChatMessage]] = None
    model: Optional[str] = "llama2"

class ChatResponse(BaseModel):
    response: str

@router.post("/message", response_model=ChatResponse)
async def chat_message(request: ChatRequest):
    try:
        # Build the conversation context
        context = ""
        if request.history:
            for msg in request.history:
                context += f"{msg.role}: {msg.content}\n"
        context += f"user: {request.prompt}\nassistant:"
        summarizer = LocalSummarize(model_name=request.model)
        response = summarizer.summarize_text(context)
        return ChatResponse(response=response)
    except Exception as e:
        logger.error(f"Chatbot error: {e}")
        raise HTTPException(status_code=500, detail=str(e))