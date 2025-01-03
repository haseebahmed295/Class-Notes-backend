from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
# Constants for JWT
SECRET_KEY = "your_secret_key_here"  # Use a strong, random key. NEVER expose this in production.
ALGORITHM = "HS256"  # Hashing algorithm
ACCESS_TOKEN_EXPIRE_MINUTES = 15  # Access token expiration time
REFRESH_TOKEN_EXPIRE_DAYS = 7  # Refresh token expiration time



def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(days=7))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt
