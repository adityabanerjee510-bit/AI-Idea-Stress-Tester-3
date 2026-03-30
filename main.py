from fastapi.responses import FileResponse
from fastapi import FastAPI
from pathlib import Path
from fastapi.responses import FileResponse, JSONResponse
from routes import ai_service, login_signup
# from routes.login_signup import router as auth_router
# from routes.ai_service import router as ai_router
from fastapi.middleware.cors import CORSMiddleware


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(login_signup.router)
app.include_router(ai_service.router)

