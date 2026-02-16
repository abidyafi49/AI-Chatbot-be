from fastapi import FastAPI

app = FastAPI(
    title= "AI Companion App",
    description= "Backend Services",
    version= "0.1.0"
)

@app.get("/", tags=["Check"])
async def root():
    return {"status": "Online" , "message" : "Server backend ready"}

@app.get("/info", tags=["General"])
async def get_info():
    return {
        "app_name" : "AI Study Friend",
        "features": ["Theme-based chat", "Persistence history", "AI Summarization"]
    }