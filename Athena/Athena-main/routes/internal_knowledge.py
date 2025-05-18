from fastapi import APIRouter, Request, Form, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from generate_transcript_local import generate_transcript
from generate_blog_local import create_content
import os
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from fastapi import Body
from fastapi.responses import FileResponse
from typing import Optional, List
from googletrans import Translator

router = APIRouter(tags=["internal-knowledge"])
templates = Jinja2Templates(directory="templates")

class VideoInfo(BaseModel):
    date: str
    channel: str
    title: str
    video_url: str
    keywords: str

class SearchRequest(BaseModel):
    sheet_id: str
    sheet_name: str
    search_query: str

class VideoResponse(BaseModel):
    videos: List[VideoInfo]

class ProcessVideoRequest(BaseModel):
    video_url: str
    title: str

class ProcessVideoResponse(BaseModel):
    transcript: str
    blog_content: str
    audio_url: str

class TranslateRequest(BaseModel):
    text: str
    language: str

class TranslateResponse(BaseModel):
    translated_text: str

@router.get("/", response_class=HTMLResponse)
async def internal_knowledge_page(request: Request):
    return templates.TemplateResponse("internal_knowledge.html", {
        "request": request
    })

@router.post("/search", response_model=VideoResponse)
async def search_videos(request: SearchRequest):
    try:
        url = f"https://docs.google.com/spreadsheets/d/{request.sheet_id}/gviz/tq?tqx=out:csv&sheet={request.sheet_name}"
        df = pd.read_csv(url, dtype=str).fillna("")
        
        # Filter based on search query
        filtered_df = df[
            df["Channel"].str.contains(request.search_query, case=False) |
            df["Title"].str.contains(request.search_query, case=False) |
            df["Keywords"].str.contains(request.search_query, case=False)
        ]
        
        videos = []
        for _, row in filtered_df.iterrows():
            videos.append(VideoInfo(
                date=row['Date'],
                channel=row['Channel'].strip(),
                title=row['Title'].strip(),
                video_url=row['Video'],
                keywords=row['Keywords']
            ))
        
        return VideoResponse(videos=videos)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process-video", response_model=ProcessVideoResponse)
async def process_video(request: ProcessVideoRequest, background_tasks: BackgroundTasks):
    try:
        # Generate transcript
        transcript_result = generate_transcript(request.video_url)
        transcript = transcript_result["text"]
        
        # Generate blog content
        blog_content = create_content(transcript)
        
        # Audio file URL (assuming it's served statically)
        audio_url = "/static/audio.mp4"
        
        return ProcessVideoResponse(
            transcript=transcript,
            blog_content=blog_content,
            audio_url=audio_url
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = os.path.join("static", filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Audio file not found")
    return FileResponse(path=file_path, media_type="audio/mp4", filename=filename)

@router.post("/translate", response_model=TranslateResponse)
async def translate_text(request: TranslateRequest):
    try:
        translator = Translator()
        translated = await translator.translate(request.text, dest=request.language)
        return TranslateResponse(translated_text=translated.text)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
