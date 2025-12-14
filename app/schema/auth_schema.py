from pydantic import BaseModel, field_validator, Field, ConfigDict
import re

class UserCreate(BaseModel):
    user_name: str= Field(..., alias="username")
    password: str

    model_config = ConfigDict(populate_by_name=True)

    @field_validator("password")
    def validate_password(cls, v):
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")
        if not re.search(r"[A-Z]", v):
            raise ValueError("Password must contain at least one uppercase letter")
        if not re.search(r"[a-z]", v):
            raise ValueError("Password must contain at least one lowercase letter")
        if not re.search(r"\d", v):
            raise ValueError("Password must contain at least one digit")
        if not re.search(r"[@$!%*?&]", v):
            raise ValueError("Password must contain at least one special character (@$!%*?&)")
        return v

class UserOut(BaseModel):
    user_id: int
    user_name: str

    class Config:
        from_attributes = True

class UserLogin(BaseModel):
    user_name: str= Field(..., alias="username")
    password: str

    model_config = ConfigDict(populate_by_name=True)    

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str

class Token_data(BaseModel):
    user_id: int
    user_role: str

class RefreshTokenRequest(BaseModel):
    refresh_token: str

