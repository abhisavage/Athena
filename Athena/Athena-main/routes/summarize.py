from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional
from openai_summarize import LocalSummarize
from itranslate import itranslate as itrans

router = APIRouter(prefix="/summarize", tags=["summarization"])

class SummarizeRequest(BaseModel):
    text: str
    model_name: Optional[str] = "llama2"
    max_chunk_size: Optional[int] = 500
    max_combined_summary_size: Optional[int] = 4000
    language: Optional[str] = None

class SummarizeResponse(BaseModel):
    summary: str
    model_used: str

@router.post("/", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    try:
        summarizer = LocalSummarize(model_name=request.model_name)
        summary = summarizer.summarize_text(
            request.text,
            max_chunk_size=request.max_chunk_size,
            max_combined_summary_size=request.max_combined_summary_size
        )
        if request.language:
            try:
                translated_summary = itrans(summary, to_lang=request.language)
                print(f"Translating to {request.language}: {translated_summary}")
            except Exception as e:
                print(f"Translation error: {e}")
                translated_summary = None
        return SummarizeResponse(
            summary=summary,
            model_used=request.model_name
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))