from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas.auth import UserCreate, UserLogin, Token, UserResponse
from app.models.user import User
from app.models.patient import Patient
from app.services.auth_service import get_password_hash, verify_password, create_access_token, create_refresh_token
from app.services.deps import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    # Check if user already exists
    user_exists = db.query(User).filter(
        (User.email == user_in.email) | (User.phone == user_in.phone)
    ).first()
    
    if user_exists:
        raise HTTPException(status_code=409, detail="User with this email or phone already exists")

    # Has the password
    hashed_pwd = get_password_hash(user_in.password)
    
    # 1. Create User record
    new_user = User(
        email=user_in.email,
        phone=user_in.phone,
        hashed_password=hashed_pwd,
        role=user_in.role
    )
    db.add(new_user)
    db.commit()      # Commit to get new_user.id
    db.refresh(new_user)
    
    # 2. If registering as a patient, generate their Patient profile natively linked to the user
    if user_in.role == "patient":
        new_patient = Patient(
            name=user_in.name,
            email=user_in.email,
            phone=user_in.phone
        )
        db.add(new_patient)
        db.commit()
        db.refresh(new_patient)
        
        # Link the IDs
        new_user.linked_id = new_patient.id
        db.commit()
        db.refresh(new_user)

    return new_user

@router.post("/login", response_model=Token)
def login(user_credentials: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    # OAuth2PasswordRequestForm uses 'username' instead of 'email'
    user = db.query(User).filter(User.email == user_credentials.username).first()
    
    if not user or not verify_password(user_credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )
        
    # Generate tokens
    access_token = create_access_token(data={"sub": user.id, "role": user.role, "linked_id": user.linked_id})
    refresh_token = create_refresh_token(data={"sub": user.id})
    
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "refresh_token": refresh_token
    }

@router.get("/profile", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """
    Protected route. You must send the Authorization: Bearer <token> header to access this.
    """
    return current_user