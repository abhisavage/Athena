from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
import os
from routes import internal_knowledge
from routes.summarizer import router as summarizer_router
from routes.misc_tools import router as misc_tools_router
from routes.semantic_doc import router as semantic_doc_router
from routes.chatbot import router as chatbot_router

app = FastAPI(title="Athena API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create static directory if it doesn't exist
os.makedirs("static", exist_ok=True)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

# Templates
templates = Jinja2Templates(directory="templates")

# Include routers
app.include_router(internal_knowledge.router, prefix="/internal-knowledge", tags=["internal-knowledge"])
app.include_router(summarizer_router, prefix="/summarizer", tags=["summarizer"])
app.include_router(misc_tools_router, prefix="/misc-tools", tags=["misc-tools"])
app.include_router(semantic_doc_router, prefix="/semantic-doc", tags=["semantic-doc"])
app.include_router(chatbot_router, prefix="/chatbot", tags=["chatbot"])

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/internal-knowledge", response_class=HTMLResponse)
async def internal_knowledge_page(request: Request):
    return templates.TemplateResponse("internal_knowledge.html", {"request": request})

@app.get("/summarizer", response_class=HTMLResponse)
async def summarizer_page(request: Request):
    return templates.TemplateResponse("summarizer.html", {"request": request})

@app.get("/misc-tools", response_class=HTMLResponse)
async def misc_tools_page(request: Request):
    return templates.TemplateResponse("misc_tools.html", {"request": request})

@app.get("/semantic-doc", response_class=HTMLResponse)
async def semantic_doc_page(request: Request):
    return templates.TemplateResponse("semantic_doc.html", {"request": request})

@app.get("/chatbot", response_class=HTMLResponse)
async def chatbot_page(request: Request):
    return templates.TemplateResponse("chatbot.html", {"request": request})

@app.get("/health")
async def health_check():
    return JSONResponse(
        content={"status": "healthy", "message": "Service is running"},
        status_code=200
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)