from fastapi.responses import FileResponse
from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import FileResponse, JSONResponse
from routes.login_signup import router as auth_router
from routes.ai_service import router as ai_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/auth")
app.include_router(ai_router, prefix="/ai")

