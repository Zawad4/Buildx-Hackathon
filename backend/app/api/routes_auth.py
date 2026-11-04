from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User
from app.security.auth import verify_password, create_access_token, get_current_user
from app.security.schemas import UserLoginRequest, TokenResponse, UserProfile

router = APIRouter(prefix="/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
def login(login_req: UserLoginRequest, db: Session = Depends(get_db)):
    """
    Authenticate an employee and return a cryptographically signed JWT.
    """
    user = db.query(User).filter(User.username == login_req.username).first()
    if not user or not verify_password(login_req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is suspended or locked"
        )

    # Issue JWT token embedded with user identity and authorization role
    access_token = create_access_token(
        data={
            "sub": user.username,
            "role": user.role,
            "department": user.department,
            "user_id": user.id
        }
    )

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        user=UserProfile(
            id=user.id,
            username=user.username,
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            department=user.department
        )
    )

@router.get("/me", response_model=UserProfile)
def get_me(current_user: User = Depends(get_current_user)):
    """Returns profile of currently authenticated user."""
    return UserProfile(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department
    )

@router.get("/demo-users")
def get_demo_users():
    """Returns list of pre-configured demo roles for easy 1-click hackathon judging."""
    return [
        {
            "username": "support_alice",
            "name": "Alice Jenkins",
            "role": "SUPPORT",
            "department": "Customer Operations",
            "description": "Handles inquiries and dispute investigations."
        },
        {
            "username": "loan_bob",
            "name": "Bob Martinez",
            "role": "LOAN_OFFICER",
            "department": "Retail Lending",
            "description": "Reviews loan applications, credit scores, and PAN verifications."
        },
        {
            "username": "auditor_clara",
            "name": "Clara Oswald",
            "role": "COMPLIANCE_AUDITOR",
            "department": "Risk & Compliance",
            "description": "Monitors access patterns and performs compliance audits."
        },
        {
            "username": "admin_david",
            "name": "David Miller",
            "role": "ADMIN",
            "department": "Information Security",
            "description": "Inspects security incidents, locks compromised sessions."
        }
    ]

