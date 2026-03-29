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
        elif len(self.Password1) >12:
            raise HTTPException(status_code=400, detail="Password must be less than 12 characters long")
        elif self.Password1!=self.Password2:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        else:
            return self.Password1 == self.Password2
    @computed_field
    @property
    def Pssword(self) -> str:
        if self.Is_Password_Match == True:
            pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
            Password = pwd_context.hash(self.Password1)
            return Password
        else:
            raise HTTPException(status_code=400, detail="Passwords do not match")

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

    # ✅ Ensure data is dict
    if not isinstance(data, dict):
        data = {}

    # ✅ Check if user already exists
    if user.Id in data:
        raise HTTPException(status_code=400, detail="User already exists")

    # ✅ Save clean data
    data[user.Id] = {
        "Name": user.Name,
        "Email": user.Email,
        "Password": user.Pssword # store actual password
    }

    save_data(data)

    print("Incoming user:", user)  

    return JSONResponse(
        status_code=201,
        content={"message": f"User {user.Name} created successfully"}
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

    if not stored_password:
        raise HTTPException(status_code=500, detail="Password field missing")
    
    if stored_password != user.Password:
        raise HTTPException(status_code=401, detail="Invalid password")
    
    return JSONResponse(
        status_code=200,
        content={"message": "Login successful"}
    )
