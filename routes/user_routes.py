from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from db import get_db
from models import User
from repositories.User_repo import UserRepo
from schemas.User_schema import UserSchema
from schemas.Token_schemas import Token, TokenRefresh, LoginRequest
from utils.jwt_handler import create_tokens, verify_token

router = APIRouter()

# 1. Define the OAuth2 scheme (Tells FastAPI where to find the token)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# 2. Create the Dependency to get the current user
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    # Use your existing verify_token utility
    # We assume verify_token returns the payload (dict) or None
    payload = verify_token(token, token_type="access") 
    
    if not payload:
        raise credentials_exception
        
    email: str = payload.get("email")
    if email is None:
        raise credentials_exception
        
    user_repo = UserRepo(db)
    user = user_repo.get_user_by_email(email)
    
    if user is None:
        raise credentials_exception
        
    return user


@router.post("/signup")
def signup(user: UserSchema, db: Session = Depends(get_db)):
    user_repo = UserRepo(db)
    existing_user = user_repo.get_user_by_email(user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="User already exists")
    
    # Note: Ensure you hash the password here in production!
    db_user = User(email=user.email, password=user.password)
    user_repo.add_user(db_user)
    return {"message": "User signed up successfully"}


@router.post("/login", response_model=Token)
def login(credentials: LoginRequest, db: Session = Depends(get_db)):
    """Authenticate user and return access and refresh tokens."""
    user_repo = UserRepo(db)
    user = user_repo.get_user_by_email(credentials.email)
    
    if not user or user.password != credentials.password:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return create_tokens(user.id, user.email)


@router.post("/refresh", response_model=Token)
def refresh_token(token_data: TokenRefresh, db: Session = Depends(get_db)):
    """Get new access and refresh tokens using a valid refresh token."""
    payload = verify_token(token_data.refresh_token, token_type="refresh")
    
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired refresh token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_repo = UserRepo(db)
    user = user_repo.get_user_by_email(payload.get("email"))
    
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    return create_tokens(user.id, user.email)


# 3. Add the missing Endpoint
@router.get("/users/me")
def read_users_me(current_user: User = Depends(get_current_user)):
    """
    Returns the current user's profile.
    Requires a valid Access Token in the Authorization header.
    """
    return {
        "id": current_user.id,
        "email": current_user.email
    }