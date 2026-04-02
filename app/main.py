from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import chat, themes, users
from app.internal import admin
from app.db.database import engine, Base
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    

app = FastAPI(
    title= "AI Companion App",
    description= "Backend Services",
    version= "0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(chat.router)
app.include_router(themes.router)
app.include_router(admin.router)
app.include_router(users.router)

@app.get("/", tags=["Check"])
async def root():
    return {"message" : "Server backend ready"}

@app.get("/info", tags=["General"])
async def get_info():
    return {
        "app_name" : "AI Study Friend",
        "features": ["Theme-based chat", "Persistence history", "AI Summarization"]
    }

@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    