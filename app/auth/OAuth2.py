from jose import jwt,JWTError
from datetime import datetime, timedelta , timezone
from fastapi import HTTPException, Depends,status
from fastapi.security import OAuth2PasswordBearer
from app.schema.auth_schema import Token, Token_data
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/user/login")

SECRET_KEY = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_jwt_token(data: dict):      
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+ timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp":expire})
    encoded_jwt = jwt.encode(to_encode , SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(days=7)  
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token:str, credentials_exception):
    try:
        print(token)
        payload = jwt.decode(token=token, key=SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user_role = payload.get("user_role")
        if not user_id or not user_role:
            raise credentials_exception
        print(user_id,user_role)
        token_data = Token_data(user_id=user_id,user_role=user_role)

    except JWTError:
        raise credentials_exception
    
    return token_data

def verify_refresh_token(token: str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        user_role = payload.get("user_role")
        if user_id is None:
            raise credentials_exception
        return Token_data(user_id=user_id,user_role=user_role)
    except JWTError:
        raise credentials_exception


def get_current_user(token:str = Depends(oauth2_scheme)):
    print("get_current_user CALLED with token:", token)
    credentials_exception = HTTPException(status_code=401 , detail=f"Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})

    return verify_access_token(token, credentials_exception)



