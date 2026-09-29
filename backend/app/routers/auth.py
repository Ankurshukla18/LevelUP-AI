from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from ..database import get_db
from ..schemas.user import UserCreate, UserResponse, UserLogin, Token, TokenWithUser
from ..services import auth_service
from ..dependencies.auth import get_current_user
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["auth"])

@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    return auth_service.register_user(db, user)

@router.post("/login", response_model=TokenWithUser)
def login(user: UserLogin, db: Session = Depends(get_db)):
    return auth_service.authenticate_user(db, user)

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user
