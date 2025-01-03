# Pydantic models
from pydantic import BaseModel


class user_info(BaseModel):
    id: int
    full_name: str
    username: str
    email: str
    # created_at: str
class LoginToken(BaseModel):
    user_info: user_info
    access_token: str
    refresh_token: str
class User(BaseModel):
    username: str
    password: str
    

class Lecture(BaseModel):
    label: str 
    subject: str
    

class Data (BaseModel):
    subject: str
    lecture: str
    page :int
    data :str
    
class GetData(BaseModel):
    subject: str
    lecture: str
    
class token(BaseModel):
    token: str