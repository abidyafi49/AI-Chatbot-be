from fastapi import FastAPI
from app.routers import chat, themes
from app.internal import admin

app = FastAPI(
    title= "AI Companion App",
    description= "Backend Services",
    version= "0.1.0"
)

app.include_router(chat.router)
app.include_router(admin.router)

@app.get("/", tags=["Check"])
async def root():
    return {"message" : "Server backend ready"}

@app.get("/info", tags=["General"])
async def get_info():
    return {
        "app_name" : "AI Study Friend",
        "features": ["Theme-based chat", "Persistence history", "AI Summarization"]
    }