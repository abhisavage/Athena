from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
import subprocess
import logging

router = APIRouter(tags=["misc-tools"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("misc-tools")

class MiscToolRequest(BaseModel):
    topic: str
    action: str  # 'Notes' or 'Questions'
    model: Optional[str] = "llama2"

class MiscToolResponse(BaseModel):
    result: str


def generate_query(query, model="llama2"):
    try:
        result = subprocess.run(
            ["ollama", "run", model, query],
            capture_output=True,
            encoding='utf-8',
            timeout=180
        )
        return result.stdout.strip()
    except Exception as e:
        logger.error(f"Error generating query: {e}")
        return f"Error: {str(e)}"

@router.post("/misc-tools", response_model=MiscToolResponse)
async def misc_tools(request: MiscToolRequest):
    if not request.topic or not request.action:
        raise HTTPException(status_code=400, detail="Topic and action are required.")
    if request.action not in ["Notes", "Questions"]:
        raise HTTPException(status_code=400, detail="Action must be 'Notes' or 'Questions'.")
    try:
        if request.action == "Notes":
            query = f"Generate notes on the topic: {request.topic}"
        else:
            query = f"Generate a list of questions on the topic: {request.topic}"
        response = generate_query(query, model=request.model)
        return MiscToolResponse(result=response)
    except Exception as e:
        logger.error(f"Misc tool error: {e}")
        raise HTTPException(status_code=500, detail=str(e)) 