from fastapi import FastAPI, HTTPException, Path, Query
from pydantic import BaseModel, Field, computed_field
from typing import List, Optional,Annotated,Literal
import json
from pathlib import Path
from fastapi.responses import FileResponse, JSONResponse
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
import uuid

router = APIRouter()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class Login(BaseModel):
    id : Annotated[str, Field(..., description="The user's id")]
    Password : Annotated[str, Field(..., description="The user's password")]

class User(BaseModel):
    First_Name: Annotated[str, Field(..., description="The user's first name")]
    Last_Name: Annotated[str, Field(..., description="The user's last name")]
    Email: Annotated[str, Field(..., description="The user's email address")]
    Password1: Annotated[str, Field(..., description="The user's password")]
    Password2: Annotated[str, Field(..., description="Confirmation of the user's password")]

    @computed_field
    @property
    def Id(self) -> str:
        Id = str(uuid.uuid4())
        return Id
    @computed_field
    @property
    def Name(self) -> str:
        Name = self.First_Name + ' ' + self.Last_Name
        return Name
    @computed_field
    @property
    def Is_Password_Match(self) -> bool:
        if len(self.Password1) <8:
            raise HTTPException(status_code=400, detail="Password must be at least 8 characters long")
        elif len(self.Password1) > 72:
            raise HTTPException(status_code=400, detail="Password must be less than 72 characters long")
        elif self.Password1!=self.Password2:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        else:
            safe_password = self.Password1[:72]
            return pwd_context.hash(safe_password)
    @computed_field
    @property
    def Password(self) -> str:
        if self.Is_Password_Match:
            safe_password = self.Password1[:72]
            return pwd_context.hash(safe_password)
def load_data():
    data_path = Path(__file__).parent.parent / 'Database' / 'users.json'
    if data_path.exists():
        with open(data_path, 'r') as f:
            data=json.load(f)
            return data
    else:
        return {}


def save_data(data):
    data_path = Path(__file__).parent.parent / 'Database' / 'users.json'
    with open(data_path, 'w') as f:
        json.dump(data, f)



@router.post("/signup")
def signup(user: User):
    data = load_data()

    if not isinstance(data, dict):
        data = {}

    # ✅ check if email already exists (handle all formats)
    for u in data.values():
        existing_email = u.get("Email") or u.get("email")

        if existing_email == user.Email:
            raise HTTPException(status_code=400, detail="User already exists")

    # ✅ password validation
    if len(user.Password1) < 8:
        raise HTTPException(status_code=400, detail="Password too short")

    if len(user.Password1) > 72:
        raise HTTPException(status_code=400, detail="Password too long")

    if user.Password1 != user.Password2:
        raise HTTPException(status_code=400, detail="Passwords do not match")

    # ✅ create ID (same style you used before)
    user_id = user.Email.split("@")[0] + "_" + user.Password1

    # ✅ store (CONSISTENT FORMAT)
    data[user_id] = {
        "Name": user.First_Name + " " + user.Last_Name,
        "Email": user.Email,
        "Password": user.Password1   # plain (since your DB already uses plain)
    }

    save_data(data)

    return JSONResponse(
        status_code=201,
        content={"message": "Signup successful"}
    )

@router.post("/login")
def login_user(user: Login):
    data = load_data()

    if user.id not in data:
        raise HTTPException(status_code=404, detail="User not found")

    user_data = data[user.id]

    stored_password = (
        user_data.get("Password") or
        user_data.get("Pssword")
    )

    if stored_password == user.Password:
        return {"message": "Login successful"}
    else:
        raise HTTPException(status_code=401, detail="Invalid password")