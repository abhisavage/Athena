from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel
from typing import Optional
import tempfile
import os
import fitz  # PyMuPDF for PDF
import docx
import logging
from openai_summarize import LocalSummarize

router = APIRouter(tags=["semantic-doc"])

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("semantic-doc")

# In-memory storage for uploaded document text
semantic_docs = {}

class UploadResponse(BaseModel):
    doc_id: str
    text_preview: str

class QuestionRequest(BaseModel):
    doc_id: str
    question: str

class AnswerResponse(BaseModel):
    answer: str

def extract_text_from_pdf(file_path):
    text = ""
    with fitz.open(file_path) as doc:
        for page in doc:
            text += page.get_text()
    return text

def extract_text_from_docx(file_path):
    doc = docx.Document(file_path)
    return "\n".join([para.text for para in doc.paragraphs])

@router.post("/upload", response_model=UploadResponse)
async def upload_doc(file: UploadFile = File(...)):
    try:
        suffix = os.path.splitext(file.filename)[1].lower()
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp.write(await file.read())
            tmp_path = tmp.name
        if suffix == ".pdf":
            text = extract_text_from_pdf(tmp_path)
        elif suffix in [".docx", ".doc"]:
            text = extract_text_from_docx(tmp_path)
        else:
            os.unlink(tmp_path)
            raise HTTPException(status_code=400, detail="Unsupported file type. Please upload PDF or DOCX.")
        os.unlink(tmp_path)
        if not text.strip():
            raise HTTPException(status_code=400, detail="No text found in document.")
        doc_id = os.urandom(8).hex()
        semantic_docs[doc_id] = text
        return UploadResponse(doc_id=doc_id, text_preview=text[:1000] + ("..." if len(text) > 1000 else ""))
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/question", response_model=AnswerResponse)
async def ask_question(request: QuestionRequest):
    try:
        text = semantic_docs.get(request.doc_id)
        if not text:
            raise HTTPException(status_code=404, detail="Document not found. Please upload again.")
        prompt = f"Document:\n{text}\n\nQuestion: {request.question}\nAnswer in detail:"
        summarizer = LocalSummarize(model_name="llama2")
        answer = summarizer.summarize_text(prompt)
        return AnswerResponse(answer=answer)
    except Exception as e:
        logger.error(f"Question error: {e}")
        raise HTTPException(status_code=500, detail=str(e))