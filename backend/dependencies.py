from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
import bcrypt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel

import os
import json
import secrets
import string
from dotenv import load_dotenv

load_dotenv()

# Security configurations
SECRET_KEY = os.getenv("SECRET_KEY", "AURORA_SUPER_SECRET_KEY_FOR_HACKATHON")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "120"))

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None
    ward_id: Optional[str] = None

class UserData(BaseModel):
    username: str
    email: str
    full_name: str
    role: str
    ward_id: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    role: str
    ward: Optional[str] = None

def get_password_hash(password: str) -> str:
    pwd_bytes = password.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(pwd_bytes, salt)
    return hashed_password.decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    password_byte_enc = plain_password.encode('utf-8')
    hashed_password_byte_enc = hashed_password.encode('utf-8')
    return bcrypt.checkpw(password_byte_enc, hashed_password_byte_enc)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

# --- Persistence ---
USERS_FILE = "users.json"

def load_users():
    if not os.path.exists(USERS_FILE):
        # Default users if file doesn't exist
        default_users = {
            "citizen_1": {
                "username": "citizen_1",
                "email": "citizen@example.com",
                "full_name": "Ramesh Kumar",
                "hashed_password": get_password_hash("citizentest"),
                "role": "Citizen",
                "ward_id": None
            },
            "city_admin": {
                "username": "city_admin",
                "email": "admin@example.com",
                "full_name": "Municipal Commissioner",
                "hashed_password": get_password_hash("admintest"),
                "role": "City Admin",
                "ward_id": None
            },
            "sys_admin": {
                "username": "sys_admin",
                "email": "arbajkhan95673@gmail.com",
                "full_name": "Tech Ops Lead",
                "hashed_password": get_password_hash("systest"),
                "role": "System Admin",
                "ward_id": None
            }
        }
        save_users(default_users)
        return default_users
    
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

users_db = load_users()

# --- Core Security Functions ---
# Moved verify_password to top for clarity

def get_user(username_or_email: str):
    users = load_users()
    # Check by username
    if username_or_email in users:
        return users[username_or_email]
    # Check by email
    for user in users.values():
        if user.get("email") == username_or_email:
            return user
    return None

def add_user(username, email, role, ward_id=None, password=None):
    users = load_users()
    if not password:
        password = ''.join(secrets.choice(string.ascii_letters + string.digits) for i in range(12))
    
    users[username] = {
        "username": username,
        "email": email,
        "full_name": username, # Default to username
        "hashed_password": get_password_hash(password),
        "role": role,
        "ward_id": ward_id
    }
    save_users(users)
    return users[username], password

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# --- Authorization Dependencies (The Middleware) ---
async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        role: str = payload.get("role")
        ward_id: str = payload.get("ward_id")
        
        if username is None or role is None:
            raise credentials_exception
            
        token_data = TokenData(username=username, role=role, ward_id=ward_id)
    except JWTError:
        raise credentials_exception
        
    user = get_user(token_data.username)
    if user is None:
        raise credentials_exception
        
    return UserData(**user)

# Role Requirement Verification Generator
def require_role(allowed_roles: list[str]):
    def role_checker(current_user: UserData = Depends(get_current_user)):
        if current_user.role not in allowed_roles:
            
            # FIRE AUDIT LOGGING EVENT FOR UNAUTHORIZED ESCALATION ATTEMPT
            import logging
            logging.warning(f"[AUDIT] SECURITY BREACH BLOCKED: User '{current_user.username}' (Role: {current_user.role}) attempted unauthorized action requiring roles: {allowed_roles}.")
            
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operation not permitted. Required roles: {allowed_roles}. Your role: {current_user.role}"
            )
        return current_user
    return role_checker
