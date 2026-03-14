from pydantic import BaseModel
import datetime
import uuid

class UserCreate(BaseModel):
    username: str
    dob: datetime.date
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class PasswordRecover(BaseModel):
    username: str
    dob: datetime.date
    new_password: str

class ChannelCreate(BaseModel):
    title: str
    description: str

class ProfileResponse(BaseModel):
    username: str
    dob: datetime.date
    channels_count: int
