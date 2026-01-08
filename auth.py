from fastapi import FastAPI, Depends, HTTPException, status, Response, Cookie
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from datetime import datetime, timedelta
from typing import Optional

app=FastAPI()

fake_user_db ={
    "alice": {"username":"alice","password":"secret123"}
}

fake_refresh_token_db = {}

SECRET_KEY ="super-secret-key"
ALGORITHM ="HS256"
ACCESS_TOKEN_EXPIRE_MINUTES=30
REFRESH_TOKEN_EXPIRE_DAYS = 7

oauth32_schema = OAuth2PasswordBearer(tokenUrl="login")

def create_access_token(data:dict,expires_delta:Optional[timedelta]=None):
    to_encode =data.copy()
    expire =datetime.utcnow()+(expires_delta or timedelta(minutes=15))
    to_encode.update({"exp":expire,"type":"access"})
    encode_jwt =jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

def create_refresh_token(data:dict):
    to_encode =data.copy()
    expire =datetime.utcnow()+timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode.update({"exp":expire,"type":"refresh"})
    encode_jwt =jwt.encode(to_encode, SECRET_KEY,algorithm=ALGORITHM)
    return encode_jwt

def verify_token(token:str):
    try:
        payload = jwt.decode(token,SECRET_KEY,algorithm=ALGORITHM)
        username=payload.get("sub")
        if username is None:
            raise HTTPException(status_Code=status.HTTP_401_UNAUTHORIZED)
        return username
    except JWTError:
        raise HTTPException(status_Code=status.HTTP_401_UNAUTHORIZED)

@app.post("/login")
def login(form_data: OAuth2PasswordRequestForm = Depends(),response = None):
    user=fake_user_db.get(form_data.username)
    if not user or user["password"] != form_data.password:
        raise HTTPException(status_code=400,detail="Invalid credentials")
    
    access_token = create_access_token({"sub":user["username"]})
    refresh_token = create_refresh_token({"sub":user["username"]})
    fake_refresh_token_db[refresh_token]=user["username"]

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age = ACCESS_TOKEN_EXPIRE_MINUTES*60
    )
    response.set_cookie(
        key="refresh_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        max_age = REFRESH_TOKEN_EXPIRE_DAYS*24*60*60
    )
    return {"message":"Login successful!","access_token":access_token,"refresh_token":refresh_token}

@app.get("/protected")
def protected(
        token:Optional[str]=Depends(oauth32_schema),
        access_token: Optional[str]=Cookie(None)
    ):
    actual_token = token if token else access_token
    if not actual_token:
        raise HTTPException(status_code=401,detail="Missing token or cookie")

    username=verify_token(actual_token)
    return {"message":f"Hello,{username}! You are authenticated."}

@app.post("refresh")
def refresh_token(respone:Response, refresh_token:Optional[str]=Cookie(None)):
    if not refresh_token:
        raise HTTPException(status_code=401,detail="Refresh token missing")
    
    try:
        payload=jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type")!="refresh":
            raise HTTPException(status_Code=401,detail="Invalid token type")
        username=payload.get("sub")
    except JWTError:
        raise HTTPException(status_Code=401,detail="Invalid refresh token")
    if refresh_token not in fake_refresh_token_db:
        raise HTTPException(status_code=401, detail="Refresh token revoked or invalid")
    
    new_access_token=create_access_token(data={username})

    respone.set_cookie(
        key="access_token",
        value=new_access_token,
        httponly=True,
        samesit="lax"
    )
    return{"access_token":new_access_token,"message":"Token refreshed"}
