from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.config import settings
from app.models.user import User

# This tells FastAPI where the login URL is, so Swagger UI can use it
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise credentials_exception
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
        
    return user

# RBAC (Role-Based Access Control) Dependencies
def get_current_patient(current_user: User = Depends(get_current_user)):
    if current_user.role != "patient":
        raise HTTPException(status_code=403, detail="Not enough permissions. Patient role required.")
    return current_user

def get_current_doctor(current_user: User = Depends(get_current_user)):
    if current_user.role != "doctor":
        raise HTTPException(status_code=403, detail="Not enough permissions. Doctor role required.")
    return current_user