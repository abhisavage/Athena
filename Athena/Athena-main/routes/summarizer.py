from fastapi import APIRouter, HTTPException, UploadFile, File
from pydantic import BaseModel
from typing import Optional, List
import pdfplumber
import requests
from bs4 import BeautifulSoup
from languages import languages
from openai_summarize import LocalSummarize
from googletrans import Translator
import io
import logging

router = APIRouter(tags=["summarizer"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("summarizer")
translator = Translator()

class SummarizeRequest(BaseModel):
    text: str
    language: Optional[str] = None

class WebArticleRequest(BaseModel):
    url: str
    language: Optional[str] = None

class SummarizeResponse(BaseModel):
    summary: str
    translated_summary: Optional[str] = None

@router.post("/text", response_model=SummarizeResponse)
async def summarize_text(request: SummarizeRequest):
    try:
        summarizer = LocalSummarize(model_name="llama2")
        summary = summarizer.summarize_text(request.text)
        translated_summary = None
        if request.language:
            try:
                translated = await translator.translate(summary, dest=request.language)
                translated_summary = translated.text
                logger.info(f"Translating to {request.language}: {translated_summary}")
                if not translated_summary or translated_summary.strip() == summary.strip():
                    translated_summary = "Translation failed or not supported for this language."
            except Exception as e:
                logger.error(f"Translation error: {e}")
                translated_summary = f"Translation error: {e}"
        return SummarizeResponse(
            summary=summary,
            translated_summary=translated_summary
        )
    except Exception as e:
        logger.error(f"Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/pdf", response_model=SummarizeResponse)
async def summarize_pdf(
    file: UploadFile = File(...),
    language: Optional[str] = None
):
    try:
        content = await file.read()
        fulltext = ""
        with pdfplumber.open(io.BytesIO(content)) as pdf:
            for page in pdf.pages:
                fulltext += page.extract_text() or ""
        summarizer = LocalSummarize(model_name="llama2")
        summary = summarizer.summarize_text(fulltext)
        translated_summary = None
        if language:
            try:
                translated = await translator.translate(summary, dest=language)
                translated_summary = translated.text
                logger.info(f"Translating to {language}: {translated_summary}")
                if not translated_summary or translated_summary.strip() == summary.strip():
                    translated_summary = "Translation failed or not supported for this language."
            except Exception as e:
                logger.error(f"Translation error: {e}")
                translated_summary = f"Translation error: {e}"
        return SummarizeResponse(
            summary=summary,
            translated_summary=translated_summary
        )
    except Exception as e:
        logger.error(f"PDF Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/web", response_model=SummarizeResponse)
async def summarize_web(request: WebArticleRequest):
    try:
        res = requests.get(request.url)
        html_page = res.content
        soup = BeautifulSoup(html_page, 'html.parser')
        text = soup.find_all(text=True)
        output = ''
        blacklist = [
            '[document]', 'noscript', 'header', 'html', 'meta', 'head',
            'input', 'script', 'style', 'header_navMenu', 'sponsor_message', 'thread__wrapper',
        ]
        for t in text:
            if t.parent.name not in blacklist:
                output += '{} '.format(t).strip()
        fulltext = output.strip()
        summarizer = LocalSummarize(model_name="llama2")
        summary = summarizer.summarize_text(fulltext)
        translated_summary = None
        if request.language:
            try:
                translated = await translator.translate(summary, dest=request.language)
                translated_summary = translated.text
                logger.info(f"Translating to {request.language}: {translated_summary}")
                if not translated_summary or translated_summary.strip() == summary.strip():
                    translated_summary = "Translation failed or not supported for this language."
            except Exception as e:
                logger.error(f"Translation error: {e}")
                translated_summary = f"Translation error: {e}"
        return SummarizeResponse(
            summary=summary,
            translated_summary=translated_summary
        )
    except Exception as e:
        logger.error(f"Web Summarization error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/languages")
async def get_languages():
    return {"languages": languages} 