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

@app.get("/")
def read_root():
    file_path4 = Path(__file__).resolve().parent / "Frontend-2" / "index.html"
    return FileResponse(file_path4)

@app.get("/simulator.html")
def read_simulator():
    file_path3 = Path(__file__).resolve().parent / "Frontend-2" / "simulator.html"
    return FileResponse(file_path3)

@app.get("/Login.html")
def read_login():
    file_path = Path(__file__).resolve().parent / "Frontend-2" / "Login.html"
    return FileResponse(file_path)

@app.get("/Signup.html")
def read_signup():
    file_path1 = Path(__file__).resolve().parent / "Frontend-2" / "signup2.html"
    return FileResponse(file_path1)

@app.get("/Dashboard.html")
def read_dashboard():
    file_path2 = Path(__file__).resolve().parent / "Frontend-2" / "Dashboard.html"
    return FileResponse(file_path2)