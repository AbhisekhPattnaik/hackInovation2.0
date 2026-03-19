from pydantic import BaseModel

class UserCreate(BaseModel):
    name: str
    email: str
    password: str
    role: str  # doctor or patient

class RegisterRequest(BaseModel):
    name: str
    email: str
    phone_number: str
    password: str
    role: str

class UserLogin(BaseModel):
    email: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    role: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str

    class Config:
        from_attributes = True

class DoctorBasic(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True
