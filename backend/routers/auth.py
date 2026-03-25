from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from dependencies import (
    Token, create_access_token, timedelta, ACCESS_TOKEN_EXPIRE_MINUTES, 
    get_user, verify_password, require_role, UserData, add_user
)
from utils.email_utils import send_invitation_email
import logging

router = APIRouter(
    prefix="/auth",
    tags=["Authentication & RBAC"]
)

@router.post("/login", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    # Support both username and email for login
    user = get_user(form_data.username) 
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        logging.warning(f"[AUDIT] FAILED LOGIN ATTEMPT: Invalid credentials for '{form_data.username}'.")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    access_token = create_access_token(
        data={"sub": user["username"], "role": user["role"], "ward_id": user.get("ward_id")}, 
        expires_delta=access_token_expires
    )
    
    logging.info(f"[AUDIT] SUCCESSFUL LOGIN: User '{user['username']}' assigned role '{user['role']}'.")
    
    return {"access_token": access_token, "token_type": "bearer", "role": user["role"], "ward": user.get("ward_id")}

@router.post("/invite")
async def invite_user(
    email: str = Body(..., embed=True),
    role: str = Body(..., embed=True),
    ward_id: str = Body(None, embed=True),
    current_user: UserData = Depends(require_role(["System Admin", "City Admin"]))
):
    """
    Invite a new user via email. 
    System Admin can invite City Admins.
    City Admin can invite Ward Officers.
    """
    # Authorization logic
    if current_user.role == "City Admin" and role != "Ward Officer":
        raise HTTPException(status_code=403, detail="City Admins can only invite Ward Officers.")
    if current_user.role == "System Admin" and role == "Ward Officer":
         # Allowing System Admin to invite everyone for convenience
         pass
    
    # Generate unique username from email
    username = email.split('@')[0]
    
    # Check if user already exists
    if get_user(username) or get_user(email):
        raise HTTPException(status_code=400, detail="User already exists.")

    try:
        new_user, password = add_user(username, email, role, ward_id)
        
        # Send invitation email
        await send_invitation_email(email, username, password, role, ward_id)
        
        logging.info(f"[AUDIT] INVITATION SENT: {current_user.username} invited {email} as {role}.")
        return {"status": "success", "message": f"Invitation sent to {email}"}
    except Exception as e:
        logging.error(f"Failed to send invitation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to send invitation email.")

@router.post("/register")
async def register_citizen(
    email: str = Body(..., embed=True),
    full_name: str = Body(..., embed=True),
    password: str = Body(..., embed=True)
):
    """
    Public endpoint for citizens to create an account.
    """
    # Username is derived from email
    username = email.split('@')[0]
    
    # Reload users to check existence
    from dependencies import load_users, save_users, get_password_hash
    users = load_users()
    
    if username in users or any(u.get("email") == email for u in users.values()):
        raise HTTPException(status_code=400, detail="Account already exists.")

    try:
        new_user, _ = add_user(username, email, "Citizen", password=password)
        
        # Reload and update full name
        users = load_users()
        users[username]["full_name"] = full_name
        save_users(users)
        
        logging.info(f"[AUDIT] NEW CITIZEN REGISTERED: {username} ({email}).")
        return {"status": "success", "message": "Account created successfully."}
    except Exception as e:
        logging.error(f"Registration failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Registration failed.")

