from datetime import datetime, timezone, timedelta
from jose import jwt, JWTError
from fastapi import status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
from .database import db_dependency
from .models import User
from .schemas import TokenResponseData
import secrets

# Constants
SECRET_KEY = secrets.token_hex(32)  # Generate a secure random secret key
ALGORITHM = 'HS256'
TOKEN_EXPIRE_IN_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Create Access Token
def create_access_token(data: dict):
    payload = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(minutes=TOKEN_EXPIRE_IN_MINUTES)
    payload.update({"exp": expires})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Create Refresh Token
def create_refresh_token(data: dict):
    payload = data.copy()
    expires = datetime.now(timezone.utc) + timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    payload.update({"exp": expires})
    encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify Access Token
def verify_access_token(token: str, credential_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        id: str = payload.get("id")
        email: str = payload.get("email")
        if not id or not email:
            raise credential_exception
        return TokenResponseData(id=id, email=email)
    except JWTError as e:
        print(f"Token decoding error: {e}")  # Debug log
        raise credential_exception

# Dependency for OAuth2 Bearer Token
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='/login/token')

# Get Current User
def get_current_user(db: db_dependency, token: str = Depends(oauth2_bearer)):
    credential_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or expired token"
    )
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        token_data = verify_access_token(token, credential_exception)
        user = db.query(User).filter(User.id == token_data.id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
    except JWTError as e:
        print(f"JWT Error during token verification: {e}")  # Debug log
        raise credential_exception
